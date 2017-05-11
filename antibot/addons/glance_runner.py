from os.path import join

import requests
from bottle import abort, response

from antibot.addons.auth import AuthChecker, AuthResult
from antibot.addons.descriptors import AddOnDescriptor, GlanceDescriptor
from antibot.addons.tokens import TokenProvider
from antibot.addons.utils import addon_method_runner
from antibot.constants import API_ENDPOINT
from antibot.domain.api import HipchatAuth
from antibot.domain.configuration import Configuration
from antibot.domain.room import Room
from pynject import pynject, Injector

from antibot.domain.user import User


class GlanceRunner:
    def __init__(self, instance, configuration: Configuration, auth: AuthChecker, token_provider: TokenProvider,
                 addon: AddOnDescriptor, glance: GlanceDescriptor):
        self.token_provider = token_provider
        self.auth = auth
        self.instance = instance
        self.addon = addon
        self.configuration = configuration
        self.glance = glance
        self.panel_key = None
        for panel in self.addon.panels:
            if panel.name == self.glance.name:
                self.panel_key = panel.id
        for dialog in self.addon.dialogs:
            if dialog.title == self.glance.name:
                self.panel_key = dialog.id

    @property
    def descriptor(self):
        result = {
            'name': {
                'value': self.glance.name
            },
            'queryUrl': self.configuration.base_url + self.glance_path,
            'key': self.glance.id,
            'icon': {
                'url': self.configuration.base_url + self.icon_path,
                'url@2x': self.configuration.base_url + self.icon_path
            }
        }
        if self.panel_key is not None:
            result['target'] = self.panel_key
        return result

    @property
    def glance_path(self) -> str:
        return '/{addon}/glance/{id}'.format(addon=self.addon.id, id=self.glance.id)

    @property
    def icon_path(self) -> str:
        return '/{addon}/glance/{id}/icon'.format(addon=self.addon.id, id=self.glance.id)

    def run_ws(self):
        auth = self.auth.check_auth(self.addon)
        if not auth:
            abort(401)
        response.set_header('Access-Control-Allow-Origin', '*')
        return self.run(auth.user, auth.room)

    def run(self, user: User, room: Room):
        glance_view = addon_method_runner(self.glance.method, self.instance, user, room)

        data = {
            'label': {
                'type': 'html',
                'value': glance_view.text
            }}
        if glance_view.status is not None:
            data['status'] = {
                'type': 'lozenge',
                'value': {
                    'label': glance_view.status.text,
                    'type': glance_view.status.color.name
                }
            }
        return data

    def update(self, room: Room):
        auth = HipchatAuth(self.token_provider.get_token(self.addon, room).access_token)
        glance = self.run(None, room)
        data = {
            'glance': [
                {
                    'content': glance,
                    'key': self.glance.id
                }
            ]
        }
        requests.post(join(API_ENDPOINT, 'addon/ui/room/{}'.format(room.api_id)), json=data, auth=auth)


@pynject
class GlanceRunnerProvider:
    def __init__(self, injector: Injector, configuration: Configuration, auth: AuthChecker,
                 token_provider: TokenProvider):
        self.injector = injector
        self.auth = auth
        self.configuration = configuration
        self.token_provider = token_provider

    def get(self, addon: AddOnDescriptor, glance: GlanceDescriptor) -> GlanceRunner:
        return GlanceRunner(self.injector.get_instance(addon.cls), self.configuration, self.auth,
                            self.token_provider, addon, glance)
