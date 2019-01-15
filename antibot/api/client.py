from pyckson import parse
from pynject import singleton, pynject
from slackclient import SlackClient

from antibot.api.user import Profile
from antibot.domain.configuration import Configuration
from antibot.domain.user import User


@pynject
class SlackClientProvider:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def get(self) -> SlackClient:
        return SlackClient(self.configuration.oauth_token)


@singleton
@pynject
class SlackApi:
    def __init__(self, client: SlackClient):
        self.client = client

    def get_user(self, user_id) -> User:
        result = self.client.api_call('users.profile.get', user_id=user_id)
        profile = parse(Profile, result['profile'])
        return User(user_id, profile.display_name)
