from enum import Enum

from pyckson import no_camel_case
from typing import Optional


@no_camel_case
class MessageEvent:
    def __init__(self, channel: str, ts: str, event_ts: str, text: Optional[str] = None):
        self.channel = channel
        self.text = text
        self.ts = ts
        self.event_ts = event_ts


class EventType(Enum):
    """https://api.slack.com/events/api"""
    message = MessageEvent


class Event:
    def __init__(self, type: EventType):
        self.type = type
