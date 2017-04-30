from antibot.addons.descriptors import AddOnDescriptor, GlanceDescriptor, PanelDescriptor
from antibot.addons.glance_runner import GlanceRunner, GlanceRunnerProvider
from antibot.addons.panel_runner import PanelRunnerProvider, PanelRunner
from antibot.domain.configuration import Configuration
from pynject import pynject
from pynject.injector import Injector


class AddOnRunner:
    def __init__(self, instance, configuration: Configuration, glance_runner_provider: GlanceRunnerProvider,
                 panel_runner_provider: PanelRunnerProvider, addon: AddOnDescriptor):
        self.instance = instance
        self.addon = addon
        self.glances_runners = {glance.id: glance_runner_provider.get(addon, glance)
                                for glance in addon.glances}
        self.panels_runners = {panel.id: panel_runner_provider.get(addon, panel)
                               for panel in addon.panels}
        self.configuration = configuration

    @property
    def descriptor(self):
        return {
            'key': self.addon.id,
            'name': self.addon.name,
            'description': self.addon.description,
            'links': {
                'self': self.configuration.base_url + self.descriptor_path
            },
            'capabilities': {
                'installable': {
                    'allowGlobal': False,
                    'allowRoom': True,
                    'installedUrl': self.configuration.base_url + self.installed_path
                },
                'hipchatApiConsumer': {
                    'scopes': [
                        'send_notification'
                    ]
                },
                'glance': [glance.descriptor for glance in self.glances_runners.values()],
                'webPanel': [panel.descriptor for panel in self.panels_runners.values()]
            }
        }

    @property
    def installed_path(self) -> str:
        return '/{id}/installed'.format(id=self.addon.id)

    @property
    def descriptor_path(self) -> str:
        return '/{id}/descriptor'.format(id=self.addon.id)

    def get_glance_runner(self, glance: GlanceDescriptor) -> GlanceRunner:
        return self.glances_runners[glance.id]

    def get_panel_runner(self, panel: PanelDescriptor) -> PanelRunner:
        return self.panels_runners[panel.id]


@pynject
class AddOnRunnerProvider:
    def __init__(self, injector: Injector, configuration: Configuration, glance_runner_provider: GlanceRunnerProvider,
                 panel_runner_provider: PanelRunnerProvider):
        self.panel_runner_provider = panel_runner_provider
        self.glance_runner_provider = glance_runner_provider
        self.configuration = configuration
        self.injector = injector
        self.cache = {}

    def get(self, addon: AddOnDescriptor) -> AddOnRunner:
        if addon.id not in self.cache:
            runner = AddOnRunner(self.injector.get_instance(addon.cls), self.configuration,
                                 self.glance_runner_provider, self.panel_runner_provider, addon)
            self.cache[addon.id] = runner
            return runner
        return self.cache[addon.id]
