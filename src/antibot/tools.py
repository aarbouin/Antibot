from datetime import datetime
from inspect import signature
from typing import Iterable

import arrow

from antibot.slack.message import Message
from antibot.slack.messages_v2 import Block


def updater(cls):
    attributes = [name for name in signature(cls.__init__).parameters.keys() if name != 'self']

    def update(self, **kwargs) -> cls:
        cls_args = {attr: getattr(self, attr) for attr in attributes}
        for k, v in kwargs.items():
            cls_args[k] = v
        return cls(**cls_args)

    setattr(cls, 'update', update)

    return cls


def today() -> datetime:
    return arrow.utcnow().floor('day').datetime


def yesterday() -> datetime:
    return arrow.utcnow().floor('day').shift(days=-1).datetime


def message(blocks: Iterable[Block], **kwargs) -> Message:
    return Message(blocks=list(blocks), **kwargs)
