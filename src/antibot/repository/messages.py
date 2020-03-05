from dataclasses import dataclass
from datetime import datetime
from typing import Iterator, Optional
from uuid import uuid4

from injector import inject
from pyckson import parse, serialize, rename
from pymongo.database import Database

from antibot.tools import today


@rename(id='_id')
@dataclass
class SlackMessage:
    id: str
    type: str
    date: datetime
    timestamp: str
    channel_id: Optional[str]

    @staticmethod
    def create_today(type: str, timestamp: str, channel_id: Optional[str] = None) -> 'SlackMessage':
        return SlackMessage(str(uuid4()), type, today(), timestamp, channel_id)


class MessagesRepository:
    @inject
    def __init__(self, db: Database):
        self.collection = db['messages']

    def find_all(self, type: str, date: Optional[datetime] = None) -> Iterator[SlackMessage]:
        query = {'type': type}
        if date is not None:
            query['date'] = date
        for item in self.collection.find(query):
            yield parse(SlackMessage, item)

    def find_one(self, type: str, date: Optional[datetime] = None) -> Optional[SlackMessage]:
        query = {'type': type}
        if date is not None:
            query['date'] = date
        doc = self.collection.find_one(query)
        if doc is not None:
            return parse(SlackMessage, doc)

    def update_timestamp(self, id: str, timestamp: str):
        self.collection.update({'_id': id}, {'$set': {'timestamp': timestamp}})

    def delete(self, id: str):
        self.collection.remove({'_id': id})

    def create(self, message: SlackMessage):
        self.collection.insert_one(serialize(message))
