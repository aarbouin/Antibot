import logging

from sleekxmpp.clientxmpp import ClientXMPP

from antibot.domain.configuration import Configuration
from antibot.repository.rooms import RoomsRepository
from antibot.repository.users import UsersRepository
from antibot.xmpp.handler import MessageHandler
from pynject import pynject, singleton


@pynject
@singleton
class HipchatXmppClient:
    def __init__(self, client: ClientXMPP, handler: MessageHandler, users_repo: UsersRepository,
                 configuration: Configuration, rooms: RoomsRepository):
        self.rooms = rooms
        self.client = client
        self.handler = handler
        self.bot_name = users_repo.get_bot_name()
        self.configuration = configuration
        self.client.add_event_handler('session_start', self.session_start)
        self.client.add_event_handler('roster_update', self.join_rooms)
        self.client.add_event_handler('groupchat_message', self.message)

    def session_start(self, event):
        self.client.send_presence()
        self.client.get_roster()

    def join_rooms(self, event):
        for room_name in self.configuration.rooms_to_join:
            room = self.rooms.find(room_name)
            if room is None:
                logging.getLogger(__name__).warning('Could not resolve room {}'.format(room_name))
                continue
            self.client.plugin['xep_0045'].joinMUC(room.jid, self.bot_name, wait=True)

    def on_presence(self, presence):
        pass

    def message(self, msg):
        if msg['delay']['stamp']:
            return
        logging.getLogger(__name__).debug('Received message : {}'.format(msg))
        self.handler.handle(msg['mucroom'], msg['mucnick'], msg['body'])

    def send_message(self, room_jid, message):
        self.client.send_message(mto=room_jid, mbody=message, mtype='groupchat')

    def run(self):
        logging.getLogger(__name__).info('Bootstrapping xmpp client')
        self.client.connect()
        self.client.process(block=True)
