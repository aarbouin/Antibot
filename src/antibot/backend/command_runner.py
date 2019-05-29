from typing import Type

from bottle import request
from pyckson import serialize
from pynject import Injector, pynject

from antibot.backend.constants import METHOD_HAS_USER_ATTR
from antibot.backend.request_checker import RequestChecker
from antibot.model.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.message import Message


@pynject
class CommandRunner:
    def __init__(self, injector: Injector, users: UsersRepository, checker: RequestChecker):
        self.injector = injector
        self.users = users
        self.checker = checker

    def run_command(self, method, plugin: Type[AntibotPlugin]):
        self.checker.check_request(request)
        instance = self.injector.get_instance(plugin)
        data = request.forms
        user = self.users.get_user(data['user_id'])

        kwargs = {}
        if getattr(method, METHOD_HAS_USER_ATTR, False):
            kwargs['user'] = user

        reply = method(instance, **kwargs)
        if isinstance(reply, Message):
            return serialize(reply)
