import logging
from typing import List

from straight.plugin import load

from antibot.domain.configuration import Configuration
from antibot.domain.plugin import AntibotPlugin
from pynject import pynject


def find_plugins(configuration: Configuration, plugin_filter: List[str]):
    plugins = load(configuration.plugins_package, subclasses=AntibotPlugin)
    for plugin in plugins:
        if len(plugin_filter) > 0 and plugin.__name__ not in plugin_filter:
            continue
        logging.info('found plugin {}'.format(plugin.__name__))
        pynject(plugin)
        yield plugin
