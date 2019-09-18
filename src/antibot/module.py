import os
from typing import List, Type

from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pynject import Module
from slack import WebClient

from antibot.backend.plugins import PluginsCollection
from antibot.model.configuration import Configuration
from antibot.slack.api import SlackClientProvider


class AntibotModule(Module):
    def __init__(self, configuration: Configuration, plugins, submodules: List[Type[Module]]):
        super().__init__()
        self.configuration = configuration
        self.plugins = plugins
        self.submodules = submodules

    def configure(self):
        for plugin in self.plugins:
            self.bind(plugin).as_singleton()
        self.bind(WebClient).to_provider(SlackClientProvider)
        self.bind(Configuration).to_instance(self.configuration)
        self.bind(PluginsCollection).to_instance(PluginsCollection(self.plugins))
        self.bind(Database).to_instance(MongoClient(os.environ['MONGO_URI'])['antibot'])
        for module in self.submodules:
            self.install(module())
