import logging
from typing import Type

from bottle import route
from pynject import pynject

from antibot.addons.command_runner import CommandRunner
from antibot.addons.descriptor import find_commands
from antibot.domain.configuration import Configuration
from antibot.domain.plugin import AntibotPlugin


@pynject
class PluginInstaller:
    def __init__(self, cmd_runner: CommandRunner, configuration: Configuration):
        self.cmd_runner = cmd_runner
        self.configuration = configuration

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for command in find_commands(plugin):
            logging.getLogger(__name__).info('Installing command {}{}'.format(self.configuration.vhost, command.route))
            route(command.route, method='POST')(lambda: self.cmd_runner.run_command(command.method, plugin))
