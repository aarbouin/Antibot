from typing import Type, Callable, Iterable

from pyckson import parse, serialize
from pynject import pynject, singleton

from antibot.backend.constants import DIALOG_SUBMIT_ID
from antibot.backend.descriptor import find_method_by_attribute
from antibot.backend.endpoint_runner import EndpointRunner
from antibot.model.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.callback import DialogSubmitPayload
from antibot.slack.channel import Channel
from antibot.slack.message import Message, DialogReply


class DialogSubmitDescriptor:
    def __init__(self, plugin: Type[AntibotPlugin], method: Callable, callback_id: str):
        self.plugin = plugin
        self.method = method
        self.callback_id = callback_id


@pynject
@singleton
class DialogSubmitRunner:
    def __init__(self, endpoints: EndpointRunner, users: UsersRepository, api: SlackApi):
        self.endpoints = endpoints
        self.users = users
        self.api = api
        self.descriptors = []

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for method, callback_id in find_method_by_attribute(plugin, DIALOG_SUBMIT_ID):
            self.descriptors.append(DialogSubmitDescriptor(plugin, method, callback_id))

    def find_callback(self, callback_id) -> Iterable[DialogSubmitDescriptor]:
        for descriptor in self.descriptors:
            if descriptor.callback_id == callback_id:
                yield descriptor

    def run(self, payload: dict):
        message = parse(DialogSubmitPayload, payload)
        for descriptor in self.find_callback(message.callback_id):
            user = self.users.get_user(message.user.id)
            channel = Channel(message.channel.id, message.channel.name)
            reply = self.endpoints.run(descriptor.plugin, descriptor.method,
                                       user=user, channel=channel,
                                       callback_id=message.callback_id,
                                       state=message.state,
                                       **message.submission)
            if isinstance(reply, DialogReply):
                return serialize(reply)
            if isinstance(reply, Message):
                self.api.respond(message.response_url, reply)
