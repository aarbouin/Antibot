from dataclasses import dataclass
from inspect import getmembers
from typing import Iterator, Optional, Callable, Iterable, Any, Tuple

from antibot.internal.backend.constants import CMD_ATTR, WS_ATTR


@dataclass
class CommandDescriptor:
    route: str
    method: Callable


def find_commands(cls) -> Iterator[CommandDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, CMD_ATTR):
            yield getattr(method, CMD_ATTR)


@dataclass
class BlockActionOptions:
    block_id: Optional[str]
    action_id: Optional[str]


def find_method_by_attribute(cls, attr) -> Iterable[Tuple[Callable, Any]]:
    for name, method in getmembers(cls):
        if hasattr(method, attr):
            yield (method, getattr(method, attr))


@dataclass
class WsDescriptor:
    route: str
    http_method: str
    method: Callable


def find_ws(cls) -> Iterator[WsDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, WS_ATTR):
            yield getattr(method, WS_ATTR)
