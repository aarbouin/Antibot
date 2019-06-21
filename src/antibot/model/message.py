from datetime import datetime
from typing import Optional
from uuid import uuid4

from autovalue import autovalue
from pyckson import rename

from antibot.tools import today


@autovalue
@rename(_id='_id')
class SlackMessage:
    def __init__(self, _id: str, type: str, date: datetime, timestamp: str, channel_id: Optional[str] = None):
        self._id = _id
        self.type = type
        self.date = date
        self.timestamp = timestamp
        self.channel_id = channel_id

    @staticmethod
    def create_today(type: str, timestamp: str, channel_id: Optional[str] = None) -> 'SlackMessage':
        return SlackMessage(str(uuid4()), type, today(), timestamp, channel_id)
