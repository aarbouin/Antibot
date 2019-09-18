import os
import traceback
from contextlib import contextmanager
from datetime import datetime
from json import dumps
from typing import Optional, Callable

from pynject import pynject, singleton

from antibot.slack.api import SlackApi


class DebugHook:
    def on_query(self, query: dict) -> bool:
        """Return False to dismiss the hook"""
        pass


class QueryCatcher(DebugHook):
    def __init__(self, count: int, callback: Callable[[dict], None]):
        self.count = count
        self.callback = callback

    def on_query(self, query: dict):
        self.callback(query)
        self.count -= 1
        if self.count == 0:
            return False
        return True


@pynject
@singleton
class Debugger:
    def __init__(self, api: SlackApi):
        self.api = api
        self.hooks = []

    @contextmanager
    def wrap(self, query: Optional[dict] = None):
        try:
            self.process_hooks(query)
            yield
        except Exception:
            if os.environ.get('ENV', 'prod') != 'dev':
                date = datetime.now().isoformat()
                self.api.upload_file('bot',
                                     filename='error-{}-stacktrace.txt'.format(date),
                                     title='Antibot error stacktrace from {}'.format(date),
                                     content=traceback.format_exc().encode('utf-8'))
                if query:
                    self.api.upload_file('bot',
                                         filename='error-{}-query.json'.format(date),
                                         title='Antibot error query from {}'.format(date),
                                         content=dumps(query, indent=2).encode('utf-8'))
            raise

    def process_hooks(self, query: dict):
        for hook in self.hooks:
            res = hook.on_query(query)
            if not res:
                self.hooks.remove(hook)

    def add_hook(self, hook: DebugHook):
        self.hooks.append(hook)
