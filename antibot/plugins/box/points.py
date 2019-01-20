from typing import Iterable

from pyckson import parse, serialize
from pymongo.database import Database
from pynject import pynject

from antibot.model.user import User
from antibot.plugins.box.orders import Order


def compute_points(order: Order) -> int:
    total = 0
    for box in order.boxes:
        total -= box.price * 10
    if len(order.desserts) > 0:
        total -= 10
        total -= len(order.desserts[1:]) * 15
    total += 85
    return int(total)


class UserPoints:
    def __init__(self, user: User, points: int):
        self.user = user
        self.points = points


@pynject
class PointsRepository:
    def __init__(self, db: Database):
        self.collection = db['box_points']

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
        return list(self.find_all())[0]
