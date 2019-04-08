import logging
import re
from functools import partial
from typing import Type

from bottle import route
from pynject import pynject

from antibot.backend.callback_runner import CallbackRunner
from antibot.backend.command_runner import CommandRunner
from antibot.backend.descriptor import find_commands, find_callbacks, PluginCallbackDescriptor, find_ws
from antibot.backend.ws_runner import WsRunner
from antibot.model.configuration import Configuration
from antibot.model.plugin import AntibotPlugin


@pynject
class PluginInstaller:
    def __init__(self, cmd_runner: CommandRunner, configuration: Configuration, callback_runner: CallbackRunner,
                 ws_runner: WsRunner):
        self.cmd_runner = cmd_runner
        self.configuration = configuration
        self.callback_runner = callback_runner
        self.ws_runner = ws_runner

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for command in find_commands(plugin):
            logging.getLogger(__name__).info('Installing command {}{}'.format(self.configuration.vhost, command.route))
            route(command.route, method='POST')(
                partial(self.cmd_runner.run_command, method=command.method, plugin=plugin))

        for callback in find_callbacks(plugin):
            regex = re.compile(callback.id_regex)
            self.callback_runner.add_callback(PluginCallbackDescriptor(regex, callback.method, plugin))

        for ws in find_ws(plugin):
            route(ws.route, method=ws.http_method)(partial(self.ws_runner.run_ws, method=ws.method, plugin=plugin))

        route('/action', method='POST')(lambda: self.callback_runner.run_callback())
