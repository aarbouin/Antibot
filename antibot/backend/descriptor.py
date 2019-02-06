from inspect import getmembers
from typing import Iterator

from antibot.backend.constants import CMD_ATTR, CALLBACK_ATTR, WS_ATTR


class CommandDescriptor:
    def __init__(self, route, method):
        self.route = route
        self.method = method


def find_commands(cls) -> Iterator[CommandDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, CMD_ATTR):
            yield getattr(method, CMD_ATTR)


class CallbackDescriptor:
    def __init__(self, id_regex, method):
        self.id_regex = id_regex
        self.method = method


class PluginCallbackDescriptor:
    def __init__(self, id_regex, method, plugin_cls):
        self.id_regex = id_regex
        self.method = method
        self.plugin_cls = plugin_cls


def find_callbacks(cls) -> Iterator[CallbackDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, CALLBACK_ATTR):
            yield getattr(method, CALLBACK_ATTR)


class WsDescriptor:
    def __init__(self, route, http_method, method):
        self.route = route
        self.http_method = http_method
        self.method = method


def find_ws(cls) -> Iterator[WsDescriptor]:
    for name, method in getmembers(cls):
        if hasattr(method, WS_ATTR):
            yield getattr(method, WS_ATTR)
