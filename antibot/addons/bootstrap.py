import logging

from pynject import pynject, singleton

from antibot.addons.install import AddOnInstaller
from antibot.constants import ADDON_ATTR
from antibot.domain.configuration import Configuration
from antibot.flow.plugins import PluginsCollection


@pynject
@singleton
class AddOnBootstrap:
    def __init__(self, plugins: PluginsCollection, conf: Configuration, installer: AddOnInstaller):
        self.installer = installer
        self.plugins = plugins
        self.conf = conf
        self.routes = {}

    def bootstrap(self):
        logging.getLogger(__name__).info('Bootstraping AddOns')
        for plugin in self.plugins.plugins:
            if hasattr(plugin, ADDON_ATTR):
                addon = getattr(plugin, ADDON_ATTR)
                descriptor_path = self.installer.install(addon)
                self.routes[addon.name] = self.conf.base_url + descriptor_path

    def get_routes(self):
        yield from self.routes.items()
