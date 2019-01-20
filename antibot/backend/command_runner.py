from typing import Type

from bottle import request
from pyckson import serialize
from pynject import Injector, pynject

from antibot.slack.api import SlackApi
from antibot.backend.constants import METHOD_HAS_USER_ATTR
from antibot.slack.message import Message
from antibot.model.plugin import AntibotPlugin


@pynject
class CommandRunner:
    def __init__(self, injector: Injector, api: SlackApi):
        self.injector = injector
        self.api = api

    def run_command(self, method, plugin: Type[AntibotPlugin]):
        instance = self.injector.get_instance(plugin)
        data = request.forms
        user = self.api.get_user(data['user_id'])

        kwargs = {}
        if getattr(method, METHOD_HAS_USER_ATTR, False):
            kwargs['user'] = user

        reply = method(instance, **kwargs)
        if isinstance(reply, Message):
            return serialize(reply)
