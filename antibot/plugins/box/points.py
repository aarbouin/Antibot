from typing import Iterable

from pyckson import parse, serialize
from pymongo.database import Database
from pynject import pynject

from antibot.model.user import User
from antibot.plugins.box.orders import Order, OrderRepository
from antibot.tools import today


def compute_points(order: Order) -> int:
    total = 0
    for box in order.boxes:
        total -= box.price * 10
        total += 85
    if len(order.desserts) > 0:
        total -= 10
        total -= len(order.desserts[1:]) * 15
    if len(order.drinks) > 0:
        total -= 10
        total -= len(order.drinks[1:]) * 15
    for soup in order.soups:
        total -= soup.price * 10
    return int(total)


class UserPoints:
    def __init__(self, user: User, points: int):
        self.user = user
        self.points = points


@pynject
class PointsRepository:
    def __init__(self, db: Database, orders: OrderRepository):
        self.collection = db['box_points']
        self.orders = orders

    def get(self, user: User) -> UserPoints:
        document = self.collection.find_one({'user.id': user.id})
        if document is None:
            return self.create(user, 0)
        return parse(UserPoints, document)

    def update(self, user: User, add_points: int):
        self.get(user)
        self.collection.update({'user.id': user.id}, {'$inc': {'points': add_points}})

    def create(self, user: User, points: int) -> UserPoints:
        up = UserPoints(user, points)
        self.collection.insert_one(serialize(up))
        return up

    def find_all(self) -> Iterable[UserPoints]:
        for doc in self.collection.find(sort=[('points', -1)]):
            yield parse(UserPoints, doc)

    def pref_user(self) -> UserPoints:
        today_users = [order.user.id for order in self.orders.find_all(today())]
        return [up for up in self.find_all() if up.user.id in today_users][0]
