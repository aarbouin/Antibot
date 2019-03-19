import logging
import re
from functools import partial
from typing import Type

from bottle import route, request
from pynject import pynject

from antibot.backend.callback_runner import CallbackRunner
from antibot.backend.command_runner import CommandRunner
from antibot.backend.descriptor import find_commands, find_callbacks, PluginCallbackDescriptor, find_ws
from antibot.backend.descriptor import find_event_callbacks, \
    PluginEventCallbackDescriptor
from antibot.backend.event_callback_runner import EventCallbackRunner
from antibot.backend.ws_runner import WsRunner
from antibot.model.configuration import Configuration
from antibot.model.plugin import AntibotPlugin


@pynject
class PluginInstaller:
    def __init__(self, cmd_runner: CommandRunner, configuration: Configuration, callback_runner: CallbackRunner,
                 ws_runner: WsRunner, event_callback_runner: EventCallbackRunner):
        self.cmd_runner = cmd_runner
        self.configuration = configuration
        self.callback_runner = callback_runner
        self.ws_runner = ws_runner
        self.event_callback_runner = event_callback_runner

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

        for callback in find_event_callbacks(plugin):
            descriptor = PluginEventCallbackDescriptor(callback.event_type, callback.method, plugin)
            self.event_callback_runner.add_callback(descriptor)

    def install_event_callbacks(self):

        def route_event_callback():
            if request.json['type'] == 'url_verification':
                return request.json['challenge']
            elif request.json['type'] == 'event_callback':
                return self.event_callback_runner.run_callback()

        route('/event', method='POST')(route_event_callback)
