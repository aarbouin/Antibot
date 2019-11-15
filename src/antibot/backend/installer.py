import logging
from functools import partial
from typing import Type

from bottle import route
from pynject import pynject

from antibot.backend.actions.action_runner import ActionRunner
from antibot.backend.actions.block_action_runner import BlockActionRunner
from antibot.backend.actions.callback_runner import CallbackRunner
from antibot.backend.actions.dialog_cancel_runner import DialogCancelRunner
from antibot.backend.actions.dialog_submit_runner import DialogSubmitRunner
from antibot.backend.actions.view_closed_runner import ViewClosedRunner
from antibot.backend.actions.view_submit_runner import ViewSubmitRunner
from antibot.backend.command_runner import CommandRunner
from antibot.backend.descriptor import find_commands, find_ws
from antibot.backend.ws_runner import WsRunner
from antibot.model.configuration import Configuration
from antibot.model.plugin import AntibotPlugin


@pynject
class PluginInstaller:
    def __init__(self, cmd_runner: CommandRunner, configuration: Configuration,
                 callback_runner: CallbackRunner, block_action_runner: BlockActionRunner,
                 dialog_submit_runner: DialogSubmitRunner, dialog_cancel_runner: DialogCancelRunner,
                 ws_runner: WsRunner, action_runner: ActionRunner, view_closed_runner: ViewClosedRunner,
                 view_submit_runner: ViewSubmitRunner):
        self.cmd_runner = cmd_runner
        self.configuration = configuration
        self.callback_runner = callback_runner
        self.block_action_runner = block_action_runner
        self.dialog_submit_runner = dialog_submit_runner
        self.dialog_cancel_runner = dialog_cancel_runner
        self.ws_runner = ws_runner
        self.action_runner = action_runner
        self.view_closed_runner = view_closed_runner
        self.view_submit_runner = view_submit_runner

    def install_plugin(self, plugin: Type[AntibotPlugin]):
        for command in find_commands(plugin):
            logging.getLogger(__name__).info('Installing command {}{}'.format(self.configuration.vhost, command.route))
            route(command.route, method='POST')(
                partial(self.cmd_runner.run_command, method=command.method, plugin=plugin))

        self.callback_runner.install_plugin(plugin)
        self.block_action_runner.install_plugin(plugin)
        self.dialog_submit_runner.install_plugin(plugin)
        self.dialog_cancel_runner.install_plugin(plugin)
        self.view_closed_runner.install_plugin(plugin)
        self.view_submit_runner.install_plugin(plugin)

        for ws in find_ws(plugin):
            route(ws.route, method=ws.http_method)(partial(self.ws_runner.run_ws, method=ws.method, plugin=plugin))

        route('/action', method='POST')(lambda: self.action_runner.run())
