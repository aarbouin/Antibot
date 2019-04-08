from json import dumps
from typing import Iterator

from bottle import request
from pyckson import loads
from pynject import Injector, pynject

from antibot.backend.constants import METHOD_HAS_EVENT_ATTR
from antibot.backend.descriptor import PluginEventCallbackDescriptor
from antibot.slack.event import Event, EventType


@pynject
class EventCallbackRunner:
    def __init__(self, injector: Injector):
        self.injector = injector
        self.callbacks = []

    def add_callback(self, callback: PluginEventCallbackDescriptor):
        self.callbacks.append(callback)

    def find_callback(self, event_type: EventType) -> Iterator[PluginEventCallbackDescriptor]:
        for callback in self.callbacks:
            if callback.event_type == event_type:
                yield callback

    def run_callback(self):
        event_json = dumps(request.json['event'])
        event = loads(Event, event_json)

        for callback in self.find_callback(event.type):
            instance = self.injector.get_instance(callback.plugin_cls)

            kwargs = {}
            if getattr(callback.method, METHOD_HAS_EVENT_ATTR, False):
                kwargs['event'] = loads(event.type.value, event_json)

            callback.method(instance, **kwargs)
