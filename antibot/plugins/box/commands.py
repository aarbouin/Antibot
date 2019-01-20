from typing import Iterator
from uuid import uuid4

from autovalue import autovalue
from pyckson import rename, parse, serialize
from pymongo.database import Database
from pynject import pynject


@autovalue
@rename(_id='_id')
class CommandMessage:
    def __init__(self, _id: str, timestamp: str):
        self._id = _id
        self.timestamp = timestamp


@pynject
class CommandMessagesRepository:
    def __init__(self, db: Database):
        self.collection = db['box_cmd_messages']

    def find_all(self) -> Iterator[CommandMessage]:
        for item in self.collection.find():
            yield parse(CommandMessage, item)

    def update_timestamp(self, id: str, timestamp: str):
        self.collection.update({'_id': id}, {'$set': {'timestamp': timestamp}})

    def delete(self, id: str):
        self.collection.remove({'_id': id})

    def create(self, timestamp: str) -> CommandMessage:
        cmd = CommandMessage(str(uuid4()), timestamp)
        self.collection.insert_one(serialize(cmd))
        return cmd
