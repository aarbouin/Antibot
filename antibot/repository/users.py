import logging

from pynject import pynject, singleton

from antibot.domain.configuration import Configuration
from antibot.domain.user import User
from antibot.flow.api import HipchatApi


@pynject
@singleton
class UsersRepository:
    def __init__(self, api: HipchatApi, configuration: Configuration):
        self.api = api
        self.configuration = configuration
        logging.getLogger(__name__).info('Listing hipchat users from api')
        self.users = list(api.list_users())
        self.users_by_name = {user.name: user for user in self.users}

    def by_name(self, name: str) -> User:
        return self.users_by_name.get(name)

    def by_id(self, id: int) -> User:
        for user in self.users:
            if user.api_id == id:
                return user

    def get_bot_name(self) -> str:
        for user in self.users:
            if user.jid == self.configuration.jid:
                return user.name
        return 'Default Bot Name'
