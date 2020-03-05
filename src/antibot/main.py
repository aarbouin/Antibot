import logging

import bottle as bottle
from injector import Injector, inject

from antibot.internal.backend.installer import PluginInstaller
from antibot.internal.module import AntibotModule
from antibot.internal.plugins import find_plugins, find_modules, PluginsCollection
from antibot.internal.scheduler import Scheduler


class Main:
    @inject
    def __init__(self, scheduler: Scheduler, plugins: PluginsCollection, installer: PluginInstaller):
        self.scheduler = scheduler
        self.plugins = plugins
        self.installer = installer

    def run(self):
        for plugin in self.plugins:
            self.installer.install_plugin(plugin)
        self.scheduler.bootstrap()
        bottle.run(port=5001, host='0.0.0.0', debug=True)


def run():
    logging.basicConfig(level=logging.INFO)

    module = AntibotModule(list(find_plugins()), list(find_modules()))
    injector = Injector(module)

    main = injector.get(Main)
    main.run()


if __name__ == '__main__':
    run()
