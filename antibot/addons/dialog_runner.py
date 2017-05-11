from bottle import abort, response
from pynject import pynject, Injector

from antibot.addons.auth import AuthChecker
from antibot.addons.descriptors import AddOnDescriptor, DialogDescriptor
from antibot.addons.utils import addon_method_runner
from antibot.domain.configuration import Configuration
from antibot.domain.room import Room
from antibot.domain.user import User


class DialogRunner:
    def __init__(self, instance, configuration: Configuration, auth: AuthChecker, addon: AddOnDescriptor,
                 dialog: DialogDescriptor):
        self.auth = auth
        self.instance = instance
        self.addon = addon
        self.configuration = configuration
        self.dialog = dialog

    @property
    def descriptor(self):
        options = {}
        if self.dialog.primary:
            options['primaryAction'] = {
                'key': self.dialog.primary.key,
                'name': {
                    'value': self.dialog.primary.text
                }
            }
        if self.dialog.secondary:
            options['secondaryActions'] = {
                'key': self.dialog.secondary.key,
                'name': {
                    'value': self.dialog.secondary.text
                }
            }
        if self.dialog.width and self.dialog.height:
            options['size'] = {
                'width': self.dialog.width,
                'height': self.dialog.height
            }
        return {
            'title': {
                'value': self.dialog.title
            },
            'url': self.configuration.base_url + self.dialog_path,
            'key': self.dialog.id,
            'options': options
        }

    @property
    def dialog_path(self) -> str:
        return '/{addon}/dialog/{id}'.format(addon=self.addon.id, id=self.dialog.id)

    def run_ws(self):
        auth = self.auth.check_auth(self.addon)
        if not auth:
            abort(401)
        response.set_header('Access-Control-Allow-Origin', '*')
        return self.run(auth.user, auth.room)

    def run(self, user: User, room: Room):
        return addon_method_runner(self.dialog.method, self.instance, user, room)


@pynject
class DialogRunnerProvider:
    def __init__(self, injector: Injector, configuration: Configuration, auth: AuthChecker):
        self.injector = injector
        self.auth = auth
        self.configuration = configuration

    def get(self, addon: AddOnDescriptor, dialog: DialogDescriptor) -> DialogRunner:
        return DialogRunner(self.injector.get_instance(addon.cls), self.configuration, self.auth, addon, dialog)
