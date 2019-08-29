import json

from bottle import request
from pynject import pynject, singleton

from antibot.backend.actions.block_action_runner import BlockActionRunner
from antibot.backend.actions.callback_runner import CallbackRunner
from antibot.backend.actions.dialog_cancel_runner import DialogCancelRunner
from antibot.backend.actions.dialog_submit_runner import DialogSubmitRunner
from antibot.backend.debugger import Debugger
from antibot.backend.request_checker import RequestChecker
from antibot.repository.users import UsersRepository


@pynject
@singleton
class ActionRunner:
    def __init__(self, users: UsersRepository, checker: RequestChecker,
                 callbacks: CallbackRunner, block_actions: BlockActionRunner,
                 dialog_submits: DialogSubmitRunner, dialog_cancels: DialogCancelRunner,
                 debugger: Debugger):
        self.users = users
        self.callbacks = callbacks
        self.block_actions = block_actions
        self.dialog_submits = dialog_submits
        self.dialog_cancels = dialog_cancels
        self.checker = checker
        self.debugger = debugger

    def run(self):
        self.checker.check_request(request)

        json_data = json.loads(request.forms['payload'])

        with self.debugger.wrap(json_data):
            if json_data['type'] == 'block_actions':
                self.block_actions.run_callback(json_data)
            elif json_data['type'] == 'dialog_submission':
                self.dialog_submits.run(json_data)
            elif json_data['type'] == 'dialog_cancellation':
                self.dialog_cancels.run(json_data)
            else:
                self.callbacks.run_callback(json_data)
