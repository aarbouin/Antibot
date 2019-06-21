from inspect import getmembers
from typing import Iterator, Optional, Callable, Iterable, Any, Tuple

from autovalue import autovalue

from antibot.backend.constants import CMD_ATTR, WS_ATTR


class CommandDescriptor:
    def __init__(self, route, method):
        self.route = route
        self.method = method


def find_commands(cls) -> Iterator[CommandDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, CMD_ATTR):
            yield getattr(method, CMD_ATTR)


@autovalue
class BlockActionOptions:
    def __init__(self, block_id: Optional[str] = None, action_id: Optional[str] = None):
        self.block_id = block_id
        self.action_id = action_id


def find_method_by_attribute(cls, attr) -> Iterable[Tuple[Callable, Any]]:
    for name, method in getmembers(cls):
        if hasattr(method, attr):
            yield (method, getattr(method, attr))


class WsDescriptor:
    def __init__(self, route, http_method, method):
        self.route = route
        self.http_method = http_method
        self.method = method


def find_ws(cls) -> Iterator[WsDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, WS_ATTR):
            yield getattr(method, WS_ATTR)
