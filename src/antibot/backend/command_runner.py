from typing import Type

from bottle import request
from pynject import pynject

from antibot.backend.endpoint_runner import EndpointRunner
from antibot.backend.request_checker import RequestChecker
from antibot.model.plugin import AntibotPlugin
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.channel import Channel
from antibot.slack.message import Message


@pynject
class CommandRunner:
    def __init__(self, endpoints: EndpointRunner, users: UsersRepository, checker: RequestChecker,
                 api: SlackApi):
        self.endpoints = endpoints
        self.users = users
        self.checker = checker
        self.api = api

    def run_command(self, method, plugin: Type[AntibotPlugin]):
        self.checker.check_request(request)

        user = self.users.get_user(request.forms['user_id'])
        channel = Channel(request.forms['channel_id'], request.forms['channel_name'])
        response_url = request.forms['response_url']
        reply = self.endpoints.run(plugin, method, user=user, channel=channel, response_url=response_url,
                                   params=request.forms['text'])

        if isinstance(reply, Message):
            return self.api.respond(response_url, reply)
