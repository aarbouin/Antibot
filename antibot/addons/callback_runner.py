import json
from typing import Iterator

from bottle import request
from pyckson import loads, serialize
from pynject import Injector, pynject

from antibot.addons.descriptor import PluginCallbackDescriptor
from antibot.api.client import SlackApi
from antibot.constants import METHOD_HAS_USER_ATTR, METHOD_HAS_CALLBACK_ID_ATTR, METHOD_HAS_ACTIONS_ATTR
from antibot.domain.callback import InteractiveMessage
from antibot.domain.message import Message


@pynject
class CallbackRunner:
    def __init__(self, injector: Injector, api: SlackApi):
        self.injector = injector
        self.api = api
        self.callbacks = []

    def add_callback(self, callback: PluginCallbackDescriptor):
        self.callbacks.append(callback)

    def find_callback(self, callback_id) -> Iterator[PluginCallbackDescriptor]:
        for callback in self.callbacks:
            if callback.id_regex.match(callback_id):
                yield callback

    def run_callback(self):
        message = loads(InteractiveMessage, request.forms['payload'])
        for callback in self.find_callback(message.callback_id):
            instance = self.injector.get_instance(callback.plugin_cls)

            kwargs = {}
            if getattr(callback.method, METHOD_HAS_CALLBACK_ID_ATTR, False):
                kwargs['callback_id'] = message.callback_id
            if getattr(callback.method, METHOD_HAS_USER_ATTR, False):
                user = self.api.get_user(message.user.id)
                kwargs['user'] = user
            if getattr(callback.method, METHOD_HAS_ACTIONS_ATTR, False):
                kwargs['actions'] = message.actions

            reply = callback.method(instance, **kwargs)
            if isinstance(reply, Message):
                return serialize(reply)
