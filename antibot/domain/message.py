from antibot.domain.room import Room
from antibot.domain.user import User


class Message:
    def __init__(self, room: Room, user: User, body: str):
        self.room = room
        self.user = user
        self.body = body
