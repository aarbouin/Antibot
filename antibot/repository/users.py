from pynject import pynject, singleton

from antibot.slack.api import SlackApi


@pynject
@singleton
class UsersRepository:
    def __init__(self, api: SlackApi):
        self.api = api
