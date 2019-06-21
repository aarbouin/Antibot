from inspect import getmembers
from threading import Thread
from time import sleep

import schedule
from pynject import Injector, pynject

from antibot.backend.constants import JOB_ATTR_DAILY
from antibot.backend.plugins import PluginsCollection


class SchedulerWatch:
    def run(self):
        while True:
            schedule.run_pending()
            sleep(5)


def find_daily_jobs(cls):
    for name, method in getmembers(cls):
        hour = getattr(method, JOB_ATTR_DAILY, None)
        if hour is not None:
            yield method, hour


@pynject
class Scheduler:
    def __init__(self, injector: Injector, plugins: PluginsCollection, watch: SchedulerWatch):
        self.plugins = plugins
        self.injector = injector
        self.watch_thread = Thread(target=watch.run)

    def bootstrap(self):
        for plugin in self.plugins.plugins:
            for method, hour in find_daily_jobs(plugin):
                print(method, hour)
                schedule.every().day.at(hour).do(self.run, plugin, method)
        self.watch_thread.start()

    def run(self, cls, method):
        instance = self.injector.get_instance(cls)
        method(instance)
