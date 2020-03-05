from dataclasses import dataclass
from typing import List, Optional

from pyckson import no_camel_case

from antibot.slack.message import Option


@no_camel_case
@dataclass
class CallbackUser:
    id: str
    name: str


@no_camel_case
@dataclass
class CallbackChannel:
    id: str
    name: str


@no_camel_case
@dataclass
class SelectedOption:
    value: str


@no_camel_case
@dataclass
class StatePayload:
    values: dict


@no_camel_case
@dataclass
class ViewPayload:
    id: str
    callback_id: str
    state: Optional[StatePayload]
    private_metadata: Optional[str]


@no_camel_case
@dataclass
class CallbackAction:
    name: str
    selected_options: List[SelectedOption] = None


@no_camel_case
@dataclass
class Container:
    message_ts: Optional[str]


@no_camel_case
@dataclass
class BlockAction:
    action_id: str
    block_id: str
    value: Optional[str]
    selected_option: Optional[Option]
    selected_date: Optional[str]
    selected_channel: Optional[str]
    selected_user: Optional[str]


@no_camel_case
@dataclass
class BlockPayload:
    user: CallbackUser
    actions: List[BlockAction]
    trigger_id: str
    container: Container
    view: Optional[ViewPayload]
    channel: Optional[CallbackChannel]
    response_url: Optional[str]


@no_camel_case
@dataclass
class ViewClosedPayload:
    def __init__(self, user: CallbackUser, view: ViewPayload):
        self.user = user
        self.view = view


@no_camel_case
@dataclass
class ViewSubmitPayload:
    def __init__(self, user: CallbackUser, view: ViewPayload):
        self.user = user
        self.view = view
