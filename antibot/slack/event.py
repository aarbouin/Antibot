from enum import Enum
from typing import Optional

from pyckson import no_camel_case


@no_camel_case
class MessageEvent:
    def __init__(self, channel: str, ts: str, event_ts: str, text: Optional[str] = None, user: Optional[str] = None,
                 bot_id: Optional[str] = None):
        self.channel = channel
        self.text = text
        self.ts = ts
        self.event_ts = event_ts
        self.user = user
        self.bot_id = bot_id


class EventType(Enum):
    """https://api.slack.com/events/api"""
    message = MessageEvent


class Event:
    def __init__(self, type: EventType):
        self.type = type
