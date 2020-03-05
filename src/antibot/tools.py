from datetime import datetime
from typing import Iterable

import arrow

from antibot.slack.message import Message, Block


def today() -> datetime:
    return arrow.utcnow().floor('day').datetime


def yesterday() -> datetime:
    return arrow.utcnow().floor('day').shift(days=-1).datetime


def message(blocks: Iterable[Block], **kwargs) -> Message:
    return Message(blocks=list(blocks), **kwargs)
