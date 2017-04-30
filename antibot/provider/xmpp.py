from pynject import pynject
from sleekxmpp import ClientXMPP

from antibot.domain.configuration import Configuration


@pynject
class XmppProvider:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def get(self):
        client = ClientXMPP(jid=self.configuration.jid,
                            password=self.configuration.password)
        client.register_plugin('xep_0045')
        client.register_plugin('xep_0203')
        return client
