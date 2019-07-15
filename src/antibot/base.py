from pynject import pynject

from antibot.decorators import ws, block_action
from antibot.model.plugin import AntibotPlugin
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
