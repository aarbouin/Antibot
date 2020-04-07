import logging
from argparse import ArgumentParser

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

    def run(self, reload: bool = False):
        for plugin in self.plugins:
            self.installer.install_plugin(plugin)
        if not reload:
            self.scheduler.bootstrap()
        bottle.run(port=5001, host='0.0.0.0', debug=True, reloader=reload)


def run():
    parser = ArgumentParser()
    parser.add_argument('-r', '--reload', action='store_true', default=False)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    module = AntibotModule(list(find_plugins()), list(find_modules()))
    injector = Injector(module)

    main = injector.get(Main)
    main.run(reload=args.reload)


if __name__ == '__main__':
    run()
