from datetime import datetime
from typing import Iterator, Optional

from pyckson import parse, serialize
from pymongo.database import Database
from pynject import pynject

from antibot.model.message import SlackMessage


@pynject
class MessagesRepository:
    def __init__(self, db: Database):
        self.collection = db['messages']

    def find_all(self, type: str, date: Optional[datetime] = None) -> Iterator[SlackMessage]:
        query = {'type': type}
        if date is not None:
            query['date'] = date
        for item in self.collection.find(query):
            yield parse(SlackMessage, item)

    def update_timestamp(self, id: str, timestamp: str):
        self.collection.update({'_id': id}, {'$set': {'timestamp': timestamp}})

    def delete(self, id: str):
        self.collection.remove({'_id': id})

    def create(self, message: SlackMessage):
        self.collection.insert_one(serialize(message))
