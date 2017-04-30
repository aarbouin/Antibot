from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pynject import Module
from sleekxmpp import ClientXMPP

from antibot.domain.configuration import Configuration
from antibot.flow.plugins import PluginsCollection
from antibot.provider.xmpp import XmppProvider
from antibot.storage import Storage, StorageFactory


class AntibotModule(Module):
    def __init__(self, configuration: Configuration, plugins):
        super().__init__()
        self.configuration = configuration
        self.plugins = plugins

    def configure(self):
        self.bind(Configuration).to_instance(self.configuration)
        self.bind(ClientXMPP).to_provider(XmppProvider)
        for plugin in self.plugins:
            self.bind(plugin).as_singleton()
        self.bind(PluginsCollection).to_instance(PluginsCollection(self.plugins))
        self.bind(Database).to_instance(MongoClient()['antibot'])
        self.bind(Storage).to_factory(StorageFactory)
