from datetime import datetime
from uuid import uuid4

from autovalue import autovalue
from pyckson import rename

from antibot.tools import today


@autovalue
@rename(_id='_id')
class SlackMessage:
    def __init__(self, _id: str, type: str, date: datetime, timestamp: str):
        self._id = _id
        self.type = type
        self.date = date
        self.timestamp = timestamp

    @staticmethod
    def create_today(type: str, timestamp: str) -> 'SlackMessage':
        return SlackMessage(str(uuid4()), type, today(), timestamp)
