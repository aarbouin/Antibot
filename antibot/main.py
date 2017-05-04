import logging
from argparse import ArgumentParser
from threading import Thread

import bottle as bottle
from pynject import pynject

from antibot.addons.bootstrap import AddOnBootstrap
from antibot.flow.api import HipchatApi
from antibot.flow.bootstrap import find_plugins
from antibot.module import AntibotModule
from antibot.provider.configuration import build_configuration
from antibot.scheduler import Scheduler
from antibot.xmpp.client import HipchatXmppClient
from pynject.injector import Injector


@pynject
class Main:
    def __init__(self, client: HipchatXmppClient, api: HipchatApi, addons: AddOnBootstrap, scheduler: Scheduler):
        self.scheduler = scheduler
        self.client = client
        self.api = api
        self.addons = addons

    def run(self):
        self.addons.bootstrap()
        self.scheduler.bootstrap()
        for id, route in self.addons.get_routes():
            logging.getLogger(__name__).info('route for plugin `{}` is {}'.format(id, route))
        thread = Thread(target=self.client.run)
        thread.start()
        bottle.run(port=5000)


def run():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument('-c', '--conf-file')

    args = parser.parse_args()

    configuration = build_configuration(args)
    plugins = find_plugins(configuration)
    antibot_module = AntibotModule(configuration, plugins)
    injector = Injector(antibot_module)

    main = injector.get_instance(Main)
    main.run()


if __name__ == '__main__':
    run()
