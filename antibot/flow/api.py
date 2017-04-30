from os.path import join

import requests
from pynject import pynject
from typing import List

from antibot.addons.addon_runner import AddOnRunnerProvider
from antibot.constants import GLANCE_ATTR, API_ENDPOINT, ADDON_ATTR
from antibot.domain.api import HipchatAuth
from antibot.domain.configuration import Configuration
from antibot.domain.room import Room
from antibot.domain.user import User
from antibot.xmpp.utils import JID

DEFAULT_PARAMS = {'max-results': 1000, 'expand': 'items'}


@pynject
class HipchatApi:
    def __init__(self, configuration: Configuration, runner_provider: AddOnRunnerProvider):
        self.runner_provider = runner_provider
        self.jid = JID(configuration.jid)
        self.auth = HipchatAuth(configuration.api_token)

    def list_users(self) -> List[User]:
        for item in requests.get(join(API_ENDPOINT, 'user'), params=DEFAULT_PARAMS, auth=self.auth).json()['items']:
            yield User(item['xmpp_jid'], item['id'], item['name'], item['mention_name'], item['title'])

    def list_rooms(self) -> List[Room]:
        for item in requests.get(join(API_ENDPOINT, 'room'), params=DEFAULT_PARAMS, auth=self.auth).json()['items']:
            yield Room(item['xmpp_jid'], item['id'], item['name'])

    def send_html_message(self, room: Room, message: str):
        data = {
            'message_format': 'html',
            'message': message
        }
        requests.post(join(API_ENDPOINT, 'room/{}/notification'.format(room.api_id)), json=data, auth=self.auth)

    def update_glance(self, glance, room: Room):
        addon_descriptor = getattr(glance, ADDON_ATTR)
        glance_descriptor = getattr(glance, GLANCE_ATTR)
        runner = self.runner_provider.get(addon_descriptor).get_glance_runner(glance_descriptor)
        runner.update(room)
