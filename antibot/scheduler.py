from inspect import getmembers
from threading import Thread
from time import sleep

import schedule
from pynject import Injector, pynject

from antibot.constants import JOB_ATTR
from antibot.flow.plugins import PluginsCollection


class SchedulerWatch:
    def run(self):
        while True:
            schedule.run_pending()
            sleep(5)


def find_jobs(cls):
    for name, method in getmembers(cls):
        job = getattr(method, JOB_ATTR, None)
        if job is not None:
            yield method, job


@pynject
class Scheduler:
    def __init__(self, injector: Injector, plugins: PluginsCollection, watch: SchedulerWatch):
        self.plugins = plugins
        self.injector = injector
        self.watch_thread = Thread(target=watch.run)

    def bootstrap(self):
        for plugin in self.plugins.plugins:
            for method, job in find_jobs(plugin):
                job.do(self.run, plugin, method)
        self.watch_thread.start()

    def run(self, cls, method):
        instance = self.injector.get_instance(cls)
        method(instance)
