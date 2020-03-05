from typing import Optional

from injector import singleton, inject

from antibot.slack.api import SlackApi
from antibot.user import User


@singleton
class UsersRepository:
    @inject
    def __init__(self, api: SlackApi):
        self.api = api
        users = list(self.api.list_users())
        self.users_by_id = {user.id: user for user in users}
        self.users_by_mail = {user.email: user for user in users}

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users_by_id.get(user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.users_by_mail.get(email)
