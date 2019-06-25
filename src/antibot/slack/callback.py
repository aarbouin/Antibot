from typing import List, Optional, Dict

from pyckson import no_camel_case

from antibot.slack.message import Option


@no_camel_case
class CallbackUser:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name


@no_camel_case
class CallbackChannel:
    def __init__(self, id: str, name: str):
        self.id = id
        self.name = name


@no_camel_case
class SelectedOption:
    def __init__(self, value: str):
        self.value = value


@no_camel_case
class CallbackAction:
    def __init__(self, name: str, selected_options: List[SelectedOption] = None):
        self.name = name
        self.selected_options = selected_options


@no_camel_case
class Container:
    def __init__(self, message_ts: str):
        self.message_ts = message_ts


@no_camel_case
class BlockAction:
    def __init__(self, action_id: str, block_id: str, value: Optional[str] = None,
                 selected_option: Optional[Option] = None, selected_date: Optional[str] = None):
        self.action_id = action_id
        self.block_id = block_id
        self.value = value
        self.selected_option = selected_option
        self.selected_date = selected_date


@no_camel_case
class BlockPayload:
    def __init__(self, user: CallbackUser, channel: CallbackChannel,
                 actions: List[BlockAction], response_url: str, trigger_id: str,
                 container: Container):
        self.user = user
        self.channel = channel
        self.actions = actions
        self.response_url = response_url
        self.trigger_id = trigger_id
        self.container = container


@no_camel_case
class DialogSubmitPayload:
    def __init__(self, callback_id: str, user: CallbackUser, channel: CallbackChannel,
                 submission: Dict[str, str], state: Optional[str] = None,
                 response_url: Optional[str] = None):
        self.callback_id = callback_id
        self.user = user
        self.channel = channel
        self.submission = submission
        self.state = state
        self.response_url = response_url


@no_camel_case
class DialogCancelPayload:
    def __init__(self, callback_id: str, user: CallbackUser, channel: CallbackChannel,
                 state: Optional[str] = None, response_url: Optional[str] = None):
        self.callback_id = callback_id
        self.user = user
        self.channel = channel
        self.state = state
        self.response_url = response_url


@no_camel_case
class CallbackPayload:
    def __init__(self, callback_id: str, user: CallbackUser, channel: CallbackChannel,
                 response_url: str, actions: List[CallbackAction] = None):
        self.callback_id = callback_id
        self.user = user
        self.channel = channel
        self.response_url = response_url
        self.actions = actions
