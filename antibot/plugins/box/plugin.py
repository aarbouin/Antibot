import re
from operator import attrgetter
from typing import Optional, List

from pynject import pynject

from antibot.api.client import SlackApi
from antibot.decorators import command, callback
from antibot.domain.callback import CallbackAction
from antibot.domain.channel import Channel
from antibot.domain.message import Message, Action, Attachment, MessageType
from antibot.domain.plugin import AntibotPlugin
from antibot.domain.user import User
from antibot.plugins.box.actions import OrderAction
from antibot.plugins.box.commands import CommandMessagesRepository, CommandMessage
from antibot.plugins.box.menu.model import Box, DessertWithFlavor
from antibot.plugins.box.menu.provider import MenuProvider
from antibot.plugins.box.orders import OrderRepository, Order
from antibot.plugins.box.tools import today
from antibot.plugins.box.ui import BoxUi


@pynject
class Box(AntibotPlugin):
    def __init__(self, menu_provider: MenuProvider, orders: OrderRepository, api: SlackApi, ui: BoxUi,
                 cmd_messages: CommandMessagesRepository):
        super().__init__('Box')
        self.menu_provider = menu_provider
        self.orders = orders
        self.api = api
        self.ui = ui
        self.cmd_messages = cmd_messages

    @property
    def menu(self):
        return self.menu_provider.get()

    @command('/box/menu')
    def display_menu(self, user: User):
        date = self.menu_provider.date
        text = '*Menu du {}*\n'.format(date)
        for box in self.menu.boxes:
            text += '• {}\n'.format(box)
        if self.menu.soup is not None:
            text += '• {}€'.format(self.menu.soup)
        text += '\n*Desserts :*\n'
        for dessert in self.menu.desserts:
            if len(dessert.flavors) > 0:
                text += '• {} ({})\n'.format(dessert.name, ', '.join(dessert.flavors))
            else:
                text += '• {}\n'.format(dessert.name)

        action = Action.button('create_order', 'Place an order', 'create_order')
        attachment = Attachment('create_order', actions=[action])
        return Message(text, attachments=[attachment])

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
                order = order.update(complete=True, in_edition=False)
                self.complete_order(channel, user, new_order)
            if action.name == OrderAction.order_cancel:
                self.orders.delete(order._id)
                return Message(delete_original=True)
            if action.name == OrderAction.order_edit:
                order = order.update(in_edition=True)
            if action.name == OrderAction.dismiss:
                return Message(delete_original=True)

        self.orders.update(order)
        return Message(self.display_order(order),
                       replace_original=True,
                       attachments=self.ui.create_order_attachments(self.menu, order))

    def complete_order(self, channel: Channel, user: User, new_order: bool):
        cmds = list(self.cmd_messages.find_all())
        if len(cmds) == 0:
            cmds = [self.display_orders(channel)]
        link = self.api.get_permalink(channel.id, cmds[-1].timestamp)
        if new_order:
            message = '{} placed an order\n<{}|View all orders>'
        else:
            message = '{} updated an order\n<{}|View all orders>'
        self.api.post_message(channel.id, message.format(user.display_name, link))
        self.update_displayed_orders(channel)

    def display_orders(self, channel: Channel) -> CommandMessage:
        orders = list(self.orders.find_all(today()))
        timestamp = self.api.post_message(channel.id, self.ui.orders_text(orders))
        return self.cmd_messages.create(timestamp)

    def update_displayed_orders(self, channel: Channel):
        orders = list(self.orders.find_all(today()))
        for cmd_message in self.cmd_messages.find_all():
            new_ts = self.api.update_message(channel.id, cmd_message.timestamp,
                                             Message(text=self.ui.orders_text(orders)))
            self.cmd_messages.update_timestamp(cmd_message._id, new_ts)

    def display_order(self, order: Order) -> str:
        items = order.boxes + order.desserts
        total_price = sum(map(attrgetter('price'), items))
        if len(items) == 0:
            return 'Your order is empty'

        items = ['• {}\n'.format(item) for item in items]

        return ''.join(items) + '\nTotal price : {}€'.format(total_price)

    def find_box(self, id) -> Optional[Box]:
        for box in self.menu.boxes:
            if repr(box) == id:
                return box

        return None

    def find_dessert(self, id) -> Optional[DessertWithFlavor]:
        for dessert in self.menu.all_desserts():
            if repr(dessert) == id:
                return dessert

        return None
