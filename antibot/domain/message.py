from enum import Enum
from typing import Optional, List

from pyckson import no_camel_case


class MessageType(Enum):
    in_channel = 'in_channel'
    ephemeral = 'ephemeral'


class ActionType(Enum):
    button = 'button'
    select = 'select'


@no_camel_case
class Option:
    def __init__(self, text: str, value: str):
        self.text = text
        self.value = value


@no_camel_case
class OptionGroup:
    def __init__(self, text: str, options: List[Option]):
        self.text = text
        self.options = options


class ActionStyle(Enum):
    default = 'default'
    primary = 'primary'
    danger = 'danger'


class Confirmation:
    def __init__(self, text: str, title: Optional[str] = None, ok_text: Optional[str] = None,
                 dismiss_text: Optional[str] = None):
        self.text = text
        self.title = title
        self.ok_text = ok_text
        self.dismiss_text = dismiss_text


@no_camel_case
class Action:
    def __init__(self, name: str, text: str, type: ActionType, value: Optional[str] = None,
                 options: List[Option] = None, option_groups: List[OptionGroup] = None,
                 style: Optional[ActionStyle] = None, confirm: Optional[Confirmation] = None):
        self.name = name
        self.text = text
        self.type = type
        self.value = value
        self.options = options
        self.option_groups = option_groups
        self.style = style
        self.confirm = confirm

    @staticmethod
    def button(name, text, value, style: Optional[ActionStyle] = None, confirm: Optional[Confirmation] = None):
        return Action(name, text, ActionType.button, value=value, style=style, confirm=confirm)

    @staticmethod
    def select(name, placeholder, options: List[Option]):
        return Action(name, placeholder, ActionType.select, options=options)

    @staticmethod
    def group_select(name, placeholder, options: List[OptionGroup]):
        return Action(name, placeholder, ActionType.select, option_groups=options)


@no_camel_case
class Attachment:
    def __init__(self, callback_id: str, text: Optional[str] = None, color: Optional[str] = None,
                 actions: List[Action] = None, fallback: Optional[str] = None):
        self.callback_id = callback_id
        self.text = text
        self.color = color
        self.actions = actions
        self.fallback = fallback


@no_camel_case
class Message:
    def __init__(self, text: Optional[str] = None, response_type: MessageType = MessageType.in_channel,
                 attachments: List[Attachment] = None, replace_original: bool = False,
                 delete_original: bool = False):
        self.text = text
        self.response_type = response_type
        self.attachments = attachments
        self.replace_original = replace_original
        self.delete_original = delete_original
