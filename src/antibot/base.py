from json import dumps

from pynject import pynject

from antibot.backend.debugger import Debugger, QueryCatcher
from antibot.decorators import ws, block_action, command
from antibot.model.plugin import AntibotPlugin
from antibot.slack.api import SlackApi
from antibot.slack.message import Message
from antibot.slack.messages_v2 import Element


@pynject
class BasePlugin(AntibotPlugin):
    def __init__(self):
        super().__init__('Base')

    @ws('/', method='GET')
    def hello(self):
        return 'it\'s working'


DISMISS_ACTION = 'dismiss'
DISMISS_BUTTON = Element.button(DISMISS_ACTION, 'Dismiss')


class DismissActionPlugin(AntibotPlugin):
    def __init__(self):
        super().__init__('DismissAction')

    @block_action(action_id=DISMISS_ACTION)
    def on_dismiss(self):
        return Message(delete_original=True)


@pynject
class DebuggerPlugin(AntibotPlugin):
    def __init__(self, debugger: Debugger, api: SlackApi):
        super().__init__('Debug')
        self.debugger = debugger
        self.api = api

    @command('/debug')
    def catch_queries(self, params: str, response_url: str):
        nb_queries = int(params)

        def callback(query: dict):
            self.api.respond(response_url, Message('```{}```'.format(dumps(query))))

        self.debugger.add_hook(QueryCatcher(nb_queries, callback))
