import logging

from pynject import pynject, singleton

from antibot.backend.installer import PluginInstaller
from antibot.backend.plugins import PluginsCollection


@pynject
@singleton
class AddOnBootstrap:
    def __init__(self, plugins: PluginsCollection, installer: PluginInstaller):
        self.installer = installer
        self.plugins = plugins

    def bootstrap(self):
        logging.getLogger(__name__).info('Bootstraping AddOns')
        for plugin in self.plugins.plugins:
            self.installer.install_plugin(plugin)

        self.installer.install_event_callbacks()
