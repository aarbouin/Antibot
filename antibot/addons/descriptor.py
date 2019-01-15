from inspect import getmembers
from typing import Iterator

from antibot.constants import CMD_ATTR


class CommandDescriptor:
    def __init__(self, route, method):
        self.route = route
        self.method = method


def find_commands(cls) -> Iterator[CommandDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, CMD_ATTR):
            yield getattr(method, CMD_ATTR)
