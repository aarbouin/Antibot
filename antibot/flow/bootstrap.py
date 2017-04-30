import logging
from straight.plugin import load

from antibot.domain.configuration import Configuration
from antibot.domain.plugin import AntibotPlugin
from pynject import pynject


def find_plugins(configuration: Configuration):
    plugins = load(configuration.plugins_package, subclasses=AntibotPlugin)
    for plugin in plugins:
        logging.info('found plugin {}'.format(plugin.__name__))
        pynject(plugin)
    return plugins
