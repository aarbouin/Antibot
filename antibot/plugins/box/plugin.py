import re
from operator import attrgetter
from typing import Optional, List

from pynject import pynject

from antibot.decorators import command, callback, daily
from antibot.model.message import SlackMessage
from antibot.model.plugin import AntibotPlugin
from antibot.model.user import User
from antibot.plugins.box.actions import OrderAction, PointsAction
from antibot.plugins.box.menu.model import Box, DessertWithFlavor, Drink
from antibot.plugins.box.menu.provider import MenuProvider
from antibot.plugins.box.orders import OrderRepository, Order
from antibot.plugins.box.points import PointsRepository, compute_points
from antibot.plugins.box.ui import BoxUi
from antibot.repository.messages import MessagesRepository
from antibot.slack.api import SlackApi
from antibot.slack.callback import CallbackAction
from antibot.slack.channel import Channel
from antibot.slack.message import Message, Action, Attachment, MessageType
from antibot.tools import today, yesterday

natcolor = '#9b0000'


@pynject
class Box(AntibotPlugin):
    def __init__(self, menu_provider: MenuProvider, orders: OrderRepository, api: SlackApi, ui: BoxUi,
                 messages: MessagesRepository, points: PointsRepository):
        super().__init__('Box')
        self.menu_provider = menu_provider
        self.orders = orders
        self.api = api
        self.ui = ui
        self.messages = messages
        self.points = points

    @property
    def menu(self):
        return self.menu_provider.get()

    @command('/box/menu')
    def display_menu(self):
        self.menu_provider.get()
        date = self.menu_provider.date
        text = '*Menu du {}*\n'.format(date)
        for box in self.menu.boxes:
            text += '• {} - {}€\n'.format(box, box.price)
        if self.menu.soup is not None:
            text += '• {} - {}€'.format(self.menu.soup, self.menu.soup.price)
        text += '\n*Desserts :*\n'
        for dessert in self.menu.desserts:
            if len(dessert.flavors) > 0:
                text += '• {} ({})\n'.format(dessert.name, ', '.join(dessert.flavors))
            else:
                text += '• {}\n'.format(dessert.name)

        action = Action.button('create_order', 'Place an order', 'create_order')
        attachment = Attachment('create_order', actions=[action])
        return Message(text, attachments=[attachment])

    @command('/box/order')
    @callback(r'^create_order$')
    def create_new_order(self, user: User):
        order = self.orders.find(today(), user)
        if order is None:
            order = self.orders.create(user)
        return Message(self.display_order(order),
                       response_type=MessageType.ephemeral,
                       attachments=self.ui.create_order_attachments(self.menu, order))

    @callback(r'^update_order_[0-9a-f-]+$')
    def update_order(self, callback_id: str, actions: List[CallbackAction], user: User, channel: Channel):
        order_id = re.match(r'^update_order_([0-9a-f-]+)$', callback_id).group(1)
        order = self.orders.get(order_id)

        for action in actions:
            if action.name == OrderAction.add_box:
                box = self.find_box(action.selected_options[0].value)
                if box is not None:
                    order = order.update(boxes=order.boxes + [box])
            if action.name == OrderAction.clear_box:
                order = order.update(boxes=[])
            if action.name == OrderAction.add_dessert:
                dessert = self.find_dessert(action.selected_options[0].value)
                if dessert is not None:
                    order = order.update(desserts=order.desserts + [dessert])
            if action.name == OrderAction.clear_dessert:
                order = order.update(desserts=[])
            if action.name == OrderAction.order_confirm:
                new_order = not order.complete
                points = self.update_points(order)
                order = order.update(complete=True, in_edition=False, points_given=points)
                self.complete_order(channel, user, new_order)
            if action.name == OrderAction.order_cancel:
                self.orders.delete(order._id)
                self.points.update(order.user, -1 * order.points_given)
                return Message(delete_original=True)
            if action.name == OrderAction.order_edit:
                order = order.update(in_edition=True)
            if action.name == OrderAction.dismiss:
                return Message(delete_original=True)
            if action.name == OrderAction.add_soup:
                order = order.update(soups=order.soups + [self.menu.soup])
            if action.name == OrderAction.add_drink:
                drink = self.find_drink(action.selected_options[0].value)
                if drink is not None:
                    order = order.update(drinks=order.drinks + [drink])
            if action.name == OrderAction.clear_others:
                order = order.update(soups=[], drinks=[])

        self.orders.update(order)
        return Message(self.display_order(order),
                       replace_original=True,
                       attachments=self.ui.create_order_attachments(self.menu, order))

    def update_points(self, order: Order) -> int:
        order_points = compute_points(order)
        add_points = order_points - order.points_given
        self.points.update(order.user, add_points)
        return order_points

    @command('/box/points')
    def display_points(self):
        text = ['• {} : {} points'.format(up.user.display_name, up.points) for up in self.points.find_all()]
        attachments = self.ui.create_points_attachment(self.points.pref_user().user)
        return Message(text='\n'.join(text), response_type=MessageType.ephemeral, attachments=attachments)

    @callback('points_actions')
    def points_callback(self, actions: List[CallbackAction], channel: Channel):
        for action in actions:
            if action.name == PointsAction.dismiss:
                return Message(delete_original=True)
            if action.name == PointsAction.free_box:
                self.give_free_box(channel)
                return Message(delete_original=True)

    def give_free_box(self, channel: Channel):
        pref_user = self.points.pref_user()
        self.points.update(pref_user.user, -85)
        message = Message(attachments=[
            Attachment('', 'A free box for {}'.format(pref_user.user.display_name), natcolor)
        ])
        self.api.post_message(channel.id, message)

    def complete_order(self, channel: Channel, user: User, new_order: bool):
        cmds = list(self.messages.find_all('orders', date=today()))
        if len(cmds) == 0:
            cmds = [self.display_orders(channel)]
        link = self.api.get_permalink(channel.id, cmds[-1].timestamp)
        if new_order:
            message = '{} placed an order\n<{}|View all orders>'
        else:
            message = '{} updated an order\n<{}|View all orders>'
        msg = Message(attachments=[
            Attachment('', message.format(user.display_name, link), natcolor)
        ])
        self.api.post_message(channel.id, msg)
        self.update_displayed_orders(channel)

    @command('/box/call')
    def display_call(self, channel: Channel):
        self.display_orders(channel)

    def display_orders(self, channel: Channel) -> SlackMessage:
        orders = list(self.orders.find_all(today()))
        timestamp = self.api.post_message(channel.id, Message(self.ui.orders_text(orders)))
        message = SlackMessage.create_today('orders', timestamp)
        self.messages.create(message)
        return message

    def update_displayed_orders(self, channel: Channel):
        orders = list(self.orders.find_all(today()))
        for cmd_message in self.messages.find_all('orders', date=today()):
            new_ts = self.api.update_message(channel.id, cmd_message.timestamp,
                                             Message(text=self.ui.orders_text(orders)))
            self.messages.update_timestamp(cmd_message._id, new_ts)

    def display_order(self, order: Order) -> str:
        items = order.all_items()
        total_price = sum(map(attrgetter('price'), items))
        if len(items) == 0:
            return 'Your order is empty'

        items = ['• {}\n'.format(item) for item in items]

        return ''.join(items) + '\nTotal price : {}€ ({} points)'.format(total_price, compute_points(order))

    def find_box(self, id) -> Optional[Box]:
        for box in self.menu.boxes:
            if repr(box) == id:
                return box

        return None

    def find_drink(self, id) -> Optional[Drink]:
        for drink in self.menu.drinks:
            if repr(drink) == id:
                return drink

        return None

    def find_dessert(self, id) -> Optional[DessertWithFlavor]:
        for dessert in self.menu.all_desserts():
            if repr(dessert) == id:
                return dessert

        return None

    @daily(hour='02:00')
    def reset(self):
        for order in self.orders.find_all(yesterday()):
            self.delete(order.id)
        for message in self.messages.find_all(type='orders', date=yesterday()):
            self.messages.delete(message._id)
