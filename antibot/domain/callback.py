from typing import List

from pyckson import no_camel_case


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
class InteractiveMessage:
    def __init__(self, callback_id: str, user: CallbackUser, channel: CallbackChannel,
                 actions: List[CallbackAction] = None):
        self.callback_id = callback_id
        self.user = user
        self.channel = channel
        self.actions = actions
