from typing import Iterator

from bottle import request
from pyckson import loads, serialize
from pynject import Injector, pynject

from antibot.backend.constants import METHOD_HAS_USER_ATTR, METHOD_HAS_CALLBACK_ID_ATTR, METHOD_HAS_ACTIONS_ATTR, \
    METHOD_HAS_CHANNEL_ATTR
from antibot.backend.descriptor import PluginCallbackDescriptor
from antibot.backend.request_checker import RequestChecker
from antibot.repository.users import UsersRepository
from antibot.slack.callback import InteractiveMessage
from antibot.slack.channel import Channel
from antibot.slack.message import Message


@pynject
class CallbackRunner:
    def __init__(self, injector: Injector, users: UsersRepository, checker: RequestChecker):
        self.injector = injector
        self.users = users
        self.callbacks = []
        self.checker = checker

    def add_callback(self, callback: PluginCallbackDescriptor):
        self.callbacks.append(callback)

    def find_callback(self, callback_id) -> Iterator[PluginCallbackDescriptor]:
        for callback in self.callbacks:
            if callback.id_regex.match(callback_id):
                yield callback

    def run_callback(self):
        self.checker.check_request(request)
        message = loads(InteractiveMessage, request.forms['payload'])
        for callback in self.find_callback(message.callback_id):
            instance = self.injector.get_instance(callback.plugin_cls)

            kwargs = {}
            if getattr(callback.method, METHOD_HAS_CALLBACK_ID_ATTR, False):
                kwargs['callback_id'] = message.callback_id
            if getattr(callback.method, METHOD_HAS_USER_ATTR, False):
                user = self.users.get_user(message.user.id)
                kwargs['user'] = user
            if getattr(callback.method, METHOD_HAS_ACTIONS_ATTR, False):
                kwargs['actions'] = message.actions
            if getattr(callback.method, METHOD_HAS_CHANNEL_ATTR, False):
                channel = Channel(message.channel.id, message.channel.name)
                kwargs['channel'] = channel

            reply = callback.method(instance, **kwargs)
            if isinstance(reply, Message):
                return serialize(reply)
