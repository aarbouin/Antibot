from typing import Iterable

import pkg_resources


class AntibotPlugin:
    def __init__(self, name):
        self.name = name


def find_plugins() -> Iterable[AntibotPlugin]:
    for entry_point in pkg_resources.iter_entry_points('antibot'):
        object = entry_point.load()
        if issubclass(object, AntibotPlugin):
            yield object
