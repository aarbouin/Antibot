import atexit
import traceback
from inspect import getmembers
from threading import Thread
from time import sleep

import schedule
from injector import inject, Injector

from antibot.internal.backend.constants import JOB_ATTR_DAILY
from antibot.internal.plugins import PluginsCollection


class SchedulerWatch:
    def __init__(self):
        self.running = True

    def run(self):
        while self.running:
            schedule.run_pending()
            sleep(1)


def find_daily_jobs(cls):
    for name, method in getmembers(cls):
        hour = getattr(method, JOB_ATTR_DAILY, None)
        if hour is not None:
            yield method, hour


class Scheduler:
    @inject
    def __init__(self, injector: Injector, plugins: PluginsCollection, watch: SchedulerWatch):
        self.plugins = plugins
        self.injector = injector
        self.watch = watch
        self.watch_thread = Thread(target=watch.run)

    def bootstrap(self):
        for plugin in self.plugins.plugins:
            for method, hour in find_daily_jobs(plugin):
                print(method, hour)
                schedule.every().day.at(hour).do(self.run, plugin, method)
        self.watch_thread.start()

        def stop():
            print('stop')
            self.watch.running = False
            self.watch_thread.join(1)

        atexit.register(lambda: stop())

    def run(self, cls, method):
        try:
            instance = self.injector.get(cls)
            method(instance)
        except Exception as e:
            traceback.print_exc()
