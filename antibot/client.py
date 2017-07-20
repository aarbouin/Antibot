from typing import List

from pynject import pynject

from antibot.addons.addon_runner import AddOnRunnerProvider
from antibot.constants import ADDON_ATTR, GLANCE_ATTR
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
    def __init__(self, xmpp: HipchatXmppClient, api: HipchatApi, rooms: RoomsRepository, quickies: QuickiesRepository,
                 runner_provider: AddOnRunnerProvider):
        self.runner_provider = runner_provider
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

    def send_text_message(self, room: Room, message: str):
        self.api.send_text_message(room, message)

    def reply(self, message: Message, reply: str):
        self.send_message(message.room, reply, [message.user])

    def update_glance(self, glance, room: Room):
        addon_descriptor = getattr(glance, ADDON_ATTR)
        glance_descriptor = getattr(glance, GLANCE_ATTR)
        runner = self.runner_provider.get(addon_descriptor).get_glance_runner(glance_descriptor)
        runner.update(room)

    def update_glance_for_user(self, glance, user: User, room: Room):
        addon_descriptor = getattr(glance, ADDON_ATTR)
        glance_descriptor = getattr(glance, GLANCE_ATTR)
        runner = self.runner_provider.get(addon_descriptor).get_glance_runner(glance_descriptor)
        runner.update(room, user)

    def get_room(self, name) -> Room:
        return self.rooms.by_name(name)

    def get_users_id_in_room(self, room: Room):
        return self.api.get_users_id_in_room(room)

    def wait_reply(self, room: Room, user: User, runner):
        matcher = AndMatcher(RoomMatcher(room.name), UserMatcher(user.name))
        self.quickies.add_quicky(QuickCommand(matcher, runner, True))
