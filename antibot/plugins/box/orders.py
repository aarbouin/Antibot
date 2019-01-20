from datetime import datetime
from typing import List, Optional, Iterator
from uuid import uuid4

from autovalue import autovalue
from pyckson import rename, serialize, parse
from pymongo.database import Database
from pynject import pynject

from antibot.model.user import User
from antibot.plugins.box.menu.model import Box, DessertWithFlavor
from antibot.plugins.box.tools import today
from antibot.tools import updater


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

    def all_items(self):
        return self.boxes + self.desserts


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

    def find_all(self, date: datetime) -> Iterator[Order]:
        for doc in self.collection.find({'date': date}):
            yield parse(Order, doc)

    def find(self, date: datetime, user: User) -> Optional[Order]:
        document = self.collection.find_one({'date': date, 'user.id': user.id})
        if document is None:
            return None
        return parse(Order, document)
