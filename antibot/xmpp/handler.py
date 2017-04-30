import logging

from pynject import pynject

from antibot.domain.message import Message
from antibot.flow.command import CommandRunner
from antibot.flow.plugins import PluginsCollection
from antibot.flow.quicks import QuickiesRepository
from antibot.repository.rooms import RoomsRepository
from antibot.repository.users import UsersRepository


@pynject
class MessageHandler:
    def __init__(self, users: UsersRepository, rooms: RoomsRepository, plugins: PluginsCollection,
                 runner: CommandRunner, quickies: QuickiesRepository):
        self.quickies = quickies
        self.users = users
        self.rooms = rooms
        self.plugins = plugins
        self.runner = runner

    def handle(self, room_jid, user_name, body):
        room = self.rooms.by_jid(room_jid)
        user = self.users.by_name(user_name)
        message = Message(room, user, body)

        for quicky in self.quickies.quickies:
            if quicky.matcher.matches(message):
                result = quicky.runner(message)
                if result and quicky.auto_delete:
                    self.quickies.remove_quicky(quicky)
        for cmd in self.plugins.commands:
            if cmd.matches(message):
                logging.getLogger(__name__).info('found command on {}'.format(cmd.method))
                self.runner.run_command(cmd, message)
