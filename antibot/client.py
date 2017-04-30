from pynject import pynject
from typing import List

from antibot.domain.message import Message
from antibot.domain.room import Room
from antibot.domain.user import User
from antibot.flow.api import HipchatApi
from antibot.flow.matchers import AndMatcher, RoomMatcher, UserMatcher
from antibot.flow.quicks import QuickiesRepository, QuickCommand
from antibot.repository.rooms import RoomsRepository
from antibot.xmpp.client import HipchatXmppClient


@pynject
class HipchatClient:
    def __init__(self, xmpp: HipchatXmppClient, api: HipchatApi, rooms: RoomsRepository, quickies: QuickiesRepository):
        self.quickies = quickies
        self.rooms = rooms
        self.xmpp = xmpp
        self.api = api

    def send_message(self, room: Room, message: str, mentions: List[User] = None):
        if mentions is not None and len(mentions) > 0:
            mentions = ' '.join(['@' + user.mention for user in mentions])
            message = mentions + ' ' + message

        self.xmpp.send_message(room.jid, message)

    def send_html_message(self, room: Room, message: str):
        self.api.send_html_message(room, message)

    def reply(self, message: Message, reply: str):
        self.send_message(message.room, reply, [message.user])

    def update_glance(self, glance_method, room: Room):
        self.api.update_glance(glance_method, room)

    def get_room(self, name) -> Room:
        return self.rooms.by_name(name)

    def wait_reply(self, room: Room, user: User, runner):
        matcher = AndMatcher(RoomMatcher(room.name), UserMatcher(user.name))
        self.quickies.add_quicky(QuickCommand(matcher, runner, True))
