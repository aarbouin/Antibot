from typing import Iterable, Type

import pkg_resources
from injector import Module

from antibot.plugin import AntibotPlugin


class PluginsCollection:
    def __init__(self, plugins):
        self.plugins = plugins

    def __iter__(self):
        return iter(self.plugins)


def find_plugins() -> Iterable[Type[AntibotPlugin]]:
    for entry_point in pkg_resources.iter_entry_points('antibot'):
        object = entry_point.load()
        if issubclass(object, AntibotPlugin):
            yield object


def find_modules() -> Iterable[Type[Module]]:
    for entry_point in pkg_resources.iter_entry_points('antibot'):
        object = entry_point.load()
        if issubclass(object, Module):
            yield object
