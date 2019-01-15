import logging

from pynject import pynject, singleton

from antibot.addons.installer import PluginInstaller
from antibot.flow.plugins import PluginsCollection


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
