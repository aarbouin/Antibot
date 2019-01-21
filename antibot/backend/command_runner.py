from typing import Type

from bottle import request
from pyckson import serialize
from pynject import Injector, pynject

from antibot.backend.constants import METHOD_HAS_USER_ATTR
from antibot.model.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.message import Message


@pynject
class CommandRunner:
    def __init__(self, injector: Injector, users: UsersRepository):
        self.injector = injector
        self.users = users

    def run_command(self, method, plugin: Type[AntibotPlugin]):
        print(method)
        print(request.route)
        instance = self.injector.get_instance(plugin)
        data = request.forms
        user = self.users.get_user(data['user_id'])

        kwargs = {}
        if getattr(method, METHOD_HAS_USER_ATTR, False):
            kwargs['user'] = user

        reply = method(instance, **kwargs)
        if isinstance(reply, Message):
            return serialize(reply)
