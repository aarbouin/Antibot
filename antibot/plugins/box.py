import re
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

import arrow
from autovalue import autovalue
from pyckson import serialize, rename, parse
from pymongo.database import Database
from pynject import pynject

from antibot.decorators import command, callback
from antibot.domain.callback import CallbackAction
from antibot.domain.message import Message, Action, Attachment, MessageType, Option, OptionGroup, ActionStyle, \
    Confirmation
from antibot.domain.plugin import AntibotPlugin
from antibot.domain.user import User
from antibot.plugins.menu.model import Box, DessertWithFlavor
from antibot.plugins.menu.provider import MenuProvider
from antibot.tools import updater


class PointCalculator:
    def __init__(self, menu):
        self.menu = menu

    def get(self, picks):
        price = 0
        for box in self.menu['boxs']:
            if picks['box'] == box['name']:
                price += box['price'] * 10
                break
        else:
            raise ValueError('could not find box {} in menu'.format(picks['box']))

        price += len(picks['desserts']) * 10
        price += len(picks['boissons']) * 10
        points = 85 - price
        return int(points)


@autovalue
@rename(_id='_id')
@updater
class Order:
    def __init__(self, _id: str, user: User, date: datetime, complete: bool = False, in_edition: bool = True,
                 boxes: List[Box] = None, desserts: List[DessertWithFlavor] = None):
        self._id = _id
        self.user = user
        self.date = date
        self.complete = complete
        self.in_edition = in_edition
        self.boxes = boxes or []
        self.desserts = desserts or []


def today() -> datetime:
    return arrow.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).datetime


@pynject
class OrderRepository:
    def __init__(self, db: Database):
        self.collection = db['box_orders']

    def create(self, user: User) -> Order:
        order = Order(str(uuid4()), user, today())
        self.collection.insert_one(serialize(order))
        return order

    def update(self, order: Order):
        self.collection.update({'_id': order._id}, serialize(order))

    def get(self, order_id: str) -> Optional[Order]:
        document = self.collection.find_one({'_id': order_id})
        if document is None:
            return None
        return parse(Order, document)

    def delete(self, order_id: str):
        self.collection.delete_one({'_id': order_id})

    def find(self, date: datetime, user: User) -> Optional[Order]:
        document = self.collection.find_one({'date': date, 'user.id': user.id})
        if document is None:
            return None
        return parse(Order, document)


@pynject
class Box(AntibotPlugin):
    def __init__(self, menu_provider: MenuProvider, orders: OrderRepository):
        super().__init__('Box')
        self.menu_provider = menu_provider
        self.orders = orders

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
                       attachments=self.create_order_attachments(order))

    @callback(r'^update_order_[0-9a-f-]+$')
    def update_order(self, callback_id: str, actions: List[CallbackAction], user: User):
        order_id = re.match(r'^update_order_([0-9a-f-]+)$', callback_id).group(1)
        order = self.orders.get(order_id)

        for action in actions:
            if action.name == 'add_box':
                box = self.find_box(action.selected_options[0].value)
                if box is not None:
                    order = order.update(boxes=order.boxes + [box])
            if action.name == 'clear_box':
                order = order.update(boxes=[])
            if action.name == 'add_dessert':
                dessert = self.find_dessert(action.selected_options[0].value)
                if dessert is not None:
                    order = order.update(desserts=order.desserts + [dessert])
            if action.name == 'clear_dessert':
                order = order.update(desserts=[])
            if action.name == 'order_confirm':
                order = order.update(complete=True, in_edition=False)
            if action.name == 'order_cancel':
                self.orders.delete(order._id)
                return Message(delete_original=True)
            if action.name == 'order_edit':
                order = order.update(in_edition=True)

        self.orders.update(order)
        return Message(self.display_order(order),
                       replace_original=True,
                       attachments=self.create_order_attachments(order))

    def create_order_attachments(self, order: Order):
        options = [Option(box.name, repr(box)) for box in self.menu.boxes]
        add_box_action = Action.select('add_box', 'Pick a box...', options)
        clear_box_action = Action.button('clear_box', 'Clear boxes', 'clear_box')
        box_attachment = Attachment('update_order_{}'.format(order._id),
                                    actions=[add_box_action, clear_box_action],
                                    text='Add a box')

        options = []
        generic_group = []
        for dessert in self.menu.desserts:
            if len(dessert.flavors) > 0:
                values = [Option(str(df), repr(df)) for df in dessert.iter_flavors()]
                group = OptionGroup(dessert.name, values)
                options.append(group)
            else:
                df = dessert.with_flavor(None)
                generic_group.append(Option(str(df), repr(df)))

        options.insert(0, OptionGroup('Simple Desserts', generic_group))
        add_dessert_action = Action.group_select('add_dessert', 'Pick a dessert...', options)
        clear_dessert_action = Action.button('clear_dessert', 'Clear desserts', 'clear_dessert')
        dessert_attachment = Attachment('update_order_{}'.format(order._id),
                                        actions=[add_dessert_action, clear_dessert_action],
                                        text='Add a dessert')

        validate_button = Action.button('order_confirm', 'Validate', 'order_confirm', ActionStyle.primary)
        cancel_button = Action.button('order_cancel', 'Cancel', 'order_cancel', ActionStyle.danger)
        edit_button = Action.button('order_edit', 'Modify', 'order_edit', ActionStyle.default)
        cancel_button_confirm = Action.button('order_cancel', 'Cancel', 'order_cancel', ActionStyle.danger,
                                              confirm=Confirmation('Really ?'))
        main_actions = []
        if not order.in_edition:
            main_actions.append(edit_button)
        else:
            main_actions.append(validate_button)
        if order.complete:
            main_actions.append(cancel_button_confirm)
        else:
            main_actions.append(cancel_button)
        main_attachment = Attachment('update_order_{}'.format(order._id),
                                     actions=main_actions,
                                     fallback='Order actions',
                                     color='warning' if order.in_edition else 'good')
        attachments = [main_attachment]
        if order.in_edition:
            attachments.extend([box_attachment, dessert_attachment])
        return attachments

    def display_order(self, order: Order):
        items = []
        if len(order.boxes) == 0:
            return 'Your order is empty'
        else:
            boxes = '\n'.join(['• {}'.format(box) for box in order.boxes])
            desserts = '\n'.join(['• {}'.format(dessert) for dessert in order.desserts])
            return '*Box :*\n' + boxes + '\n*Dessert :*\n' + desserts

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
