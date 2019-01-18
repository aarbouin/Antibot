import logging
import re
from typing import Type

from bottle import route
from pynject import pynject

from antibot.addons.callback_runner import CallbackRunner
from antibot.addons.command_runner import CommandRunner
from antibot.addons.descriptor import find_commands, find_callbacks, PluginCallbackDescriptor
from antibot.domain.configuration import Configuration
from antibot.domain.plugin import AntibotPlugin


@pynject
class PluginInstaller:
    def __init__(self, cmd_runner: CommandRunner, configuration: Configuration, callback_runner: CallbackRunner):
        self.cmd_runner = cmd_runner
        self.configuration = configuration
        self.callback_runner = callback_runner

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for command in find_commands(plugin):
            logging.getLogger(__name__).info('Installing command {}{}'.format(self.configuration.vhost, command.route))
            route(command.route, method='POST')(lambda: self.cmd_runner.run_command(command.method, plugin))

        for callback in find_callbacks(plugin):
            regex = re.compile(callback.id_regex)
            self.callback_runner.add_callback(PluginCallbackDescriptor(regex, callback.method, plugin))

        route('/action', method='POST')(lambda: self.callback_runner.run_callback())
