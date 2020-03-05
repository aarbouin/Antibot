from typing import Type

from bottle import request
from injector import inject

from antibot.internal.backend.debugger import Debugger
from antibot.internal.backend.endpoint_runner import EndpointRunner
from antibot.internal.backend.request_checker import RequestChecker
from antibot.internal.slack.channel import Channel
from antibot.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.message import Message


class CommandRunner:
    @inject
    def __init__(self, endpoints: EndpointRunner, users: UsersRepository, checker: RequestChecker,
                 api: SlackApi, debugger: Debugger):
        self.endpoints = endpoints
        self.users = users
        self.checker = checker
        self.api = api
        self.debugger = debugger

    def run_command(self, method, plugin: Type[AntibotPlugin]):
        self.checker.check_request(request)

        user = self.users.get_user(request.forms['user_id'])
        channel = Channel(request.forms['channel_id'], request.forms['channel_name'])
        response_url = request.forms['response_url']
        params = request.forms['text']

        with self.debugger.wrap({'params': params}):
            reply = self.endpoints.run(plugin, method, user=user, channel=channel, response_url=response_url,
                                       params=params)

        if isinstance(reply, Message):
            return self.api.respond(response_url, reply)
