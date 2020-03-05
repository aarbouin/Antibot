import logging
from functools import partial
from typing import Type

from bottle import route
from injector import inject

from antibot.internal.backend.actions.action_runner import ActionRunner
from antibot.internal.backend.actions.block_action_runner import BlockActionRunner
from antibot.internal.backend.actions.view_closed_runner import ViewClosedRunner
from antibot.internal.backend.actions.view_submit_runner import ViewSubmitRunner
from antibot.internal.backend.command_runner import CommandRunner
from antibot.internal.backend.descriptor import find_commands, find_ws
from antibot.internal.backend.ws_runner import WsRunner
from antibot.internal.configuration import Configuration
from antibot.plugin import AntibotPlugin


class PluginInstaller:
    @inject
    def __init__(self, cmd_runner: CommandRunner, configuration: Configuration, block_action_runner: BlockActionRunner,
                 ws_runner: WsRunner, action_runner: ActionRunner, view_closed_runner: ViewClosedRunner,
                 view_submit_runner: ViewSubmitRunner):
        self.cmd_runner = cmd_runner
        self.configuration = configuration
        self.block_action_runner = block_action_runner
        self.ws_runner = ws_runner
        self.action_runner = action_runner
        self.view_closed_runner = view_closed_runner
        self.view_submit_runner = view_submit_runner

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for command in find_commands(plugin):
            logging.getLogger(__name__).info('Installing command {}{}'.format(self.configuration.vhost, command.route))
            route(command.route, method='POST')(
                partial(self.cmd_runner.run_command, method=command.method, plugin=plugin))

        self.block_action_runner.install_plugin(plugin)
        self.view_closed_runner.install_plugin(plugin)
        self.view_submit_runner.install_plugin(plugin)

        for ws in find_ws(plugin):
            route(ws.route, method=ws.http_method)(partial(self.ws_runner.run_ws, method=ws.method, plugin=plugin))

        route('/action', method='POST')(lambda: self.action_runner.run())
