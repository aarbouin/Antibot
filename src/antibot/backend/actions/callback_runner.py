import re
from typing import Type, Callable, Iterable, Pattern

from pyckson import parse
from pynject import pynject, singleton

from antibot.backend.constants import CALLBACK_ID_REGEX
from antibot.backend.descriptor import find_method_by_attribute
from antibot.backend.endpoint_runner import EndpointRunner
from antibot.model.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.callback import CallbackPayload
from antibot.slack.channel import Channel
from antibot.slack.message import Message


class CallbackDescriptor:
    def __init__(self, plugin: Type[AntibotPlugin], method: Callable, regex: Pattern):
        self.plugin = plugin
        self.method = method
        self.regex = regex


@pynject
@singleton
class CallbackRunner:
    def __init__(self, endpoints: EndpointRunner, users: UsersRepository, api: SlackApi):
        self.endpoints = endpoints
        self.users = users
        self.api = api
        self.callbacks = []

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for method, callback_regex in find_method_by_attribute(plugin, CALLBACK_ID_REGEX):
            regex = re.compile(callback_regex)
            self.callbacks.append(CallbackDescriptor(plugin, method, regex))

    def find_callback(self, callback_id) -> Iterable[CallbackDescriptor]:
        for callback in self.callbacks:
            if callback.regex.match(callback_id):
                yield callback

    def run_callback(self, payload: dict):
        message = parse(CallbackPayload, payload)
        for callback in self.find_callback(message.callback_id):
            user = self.users.get_user(message.user.id)
            channel = Channel(message.channel.id, message.channel.name)
            reply = self.endpoints.run(callback.plugin, callback.method,
                                       user=user, channel=channel,
                                       callback_id=message.callback_id,
                                       actions=message.actions)
            if isinstance(reply, Message):
                self.api.respond(message.response_url, reply)
