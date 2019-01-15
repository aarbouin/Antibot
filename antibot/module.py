from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pynject import Module
from slackclient import SlackClient

from antibot.api.client import SlackClientProvider
from antibot.domain.configuration import Configuration
from antibot.flow.plugins import PluginsCollection


class AntibotModule(Module):
    def __init__(self, configuration: Configuration, plugins):
        super().__init__()
        self.configuration = configuration
        self.plugins = plugins

    def configure(self):
        for plugin in self.plugins:
            self.bind(plugin).as_singleton()
        self.bind(SlackClient).to_provider(SlackClientProvider)
        self.bind(Configuration).to_instance(self.configuration)
        self.bind(PluginsCollection).to_instance(PluginsCollection(self.plugins))
        self.bind(Database).to_instance(MongoClient()['antibot'])
