import logging
import os

import bottle as bottle
from pynject import pynject
from pynject.injector import Injector

from antibot.backend.bootstrap import AddOnBootstrap
from antibot.model.configuration import Configuration
from antibot.module import AntibotModule
from antibot.plugins.box.plugin import Box
from antibot.scheduler import Scheduler


@pynject
class Main:
    def __init__(self, addons: AddOnBootstrap, scheduler: Scheduler):
        self.scheduler = scheduler
        self.addons = addons

    def run(self):
        self.addons.bootstrap()
        self.scheduler.bootstrap()
        bottle.DEBUG = True
        bottle.run(port=5001, host='0.0.0.0')


def run():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("requests").setLevel(logging.DEBUG)

    configuration = Configuration(os.environ['VERIFICATION_TOKEN'],
                                  os.environ['SLACK_API_TOKEN'],
                                  os.environ.get('VHOST', 'http://localhost:5001'))
    antibot_module = AntibotModule(configuration, [Box])
    injector = Injector(antibot_module)

    main = injector.get_instance(Main)
    main.run()


if __name__ == '__main__':
    run()
