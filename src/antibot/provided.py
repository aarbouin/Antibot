from datetime import datetime
from json import dumps

from injector import inject

from antibot.decorators import ws, block_action, command
from antibot.internal.backend.debugger import Debugger, QueryCatcher
from antibot.plugin import AntibotPlugin
from antibot.slack.api import SlackApi
from antibot.slack.message import Message, Element


class BasePlugin(AntibotPlugin):
    @inject
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


class DebuggerPlugin(AntibotPlugin):
    @inject
    def __init__(self, debugger: Debugger, api: SlackApi):
        super().__init__('Debug')
        self.debugger = debugger
        self.api = api

    @command('/debug')
    def catch_queries(self, params: str):
        nb_queries = int(params)

        def callback(query: dict):
            date = datetime.now().isoformat()
            self.api.upload_file('bot',
                                 filename='debug-{}-query.json'.format(date),
                                 title='Antibot debug query from {}'.format(date),
                                 content=dumps(query, indent=2).encode('utf-8'))

        self.debugger.add_hook(QueryCatcher(nb_queries, callback))
