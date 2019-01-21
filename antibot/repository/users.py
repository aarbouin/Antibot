from typing import Optional

from pynject import pynject, singleton

from antibot.model.user import User
from antibot.slack.api import SlackApi


@pynject
@singleton
class UsersRepository:
    def __init__(self, api: SlackApi):
        self.api = api
        self.users_by_id = {user.id: user for user in self.api.list_users()}

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users_by_id.get(user_id)
