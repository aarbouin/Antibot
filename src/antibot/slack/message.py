from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Union, Iterable

from pyckson import no_camel_case


class ResponseType(Enum):
    in_channel = 'in_channel'
    ephemeral = 'ephemeral'


class ActionType(Enum):
    button = 'button'
    select = 'select'


class ActionStyle(Enum):
    default = 'default'
    primary = 'primary'
    danger = 'danger'


@no_camel_case
@dataclass
class PostMessageReply:
    channel: str
    ts: str


@no_camel_case
@dataclass
class Text:
    type: str
    text: str

    @staticmethod
    def mrkdwn(text: str) -> 'Text':
        return Text('mrkdwn', text)

    @staticmethod
    def plain(text: str) -> 'Text':
        return Text('plain_text', text)


@no_camel_case
@dataclass
class Option:
    text: Text
    value: str

    @staticmethod
    def of(value: str, text: Optional[str] = None) -> 'Option':
        text = text or value
        return Option(Text.plain(text), value)


@no_camel_case
@dataclass
class OptionGroup:
    label: Text
    options: List[Option]

    @staticmethod
    def of(label: str, options: List[Option]) -> 'OptionGroup':
        return OptionGroup(Text.plain(label), options)


@no_camel_case
@dataclass
class Confirm:
    title: Text
    text: Text
    confirm: Text
    deny: Text

    @staticmethod
    def of(title: str, text: str, confirm: str, deny: str) -> 'Confirm':
        return Confirm(Text.plain(title), Text.mrkdwn(text),
                       Text.plain(confirm), Text.plain(deny))


@no_camel_case
@dataclass
class Element:
    type: str
    action_id: str
    text: Optional[Text] = None
    options: List[Option] = None
    option_groups: List[OptionGroup] = None
    initial_option: Optional[Option] = None
    initial_date: Optional[str] = None
    initial_channel: Optional[str] = None
    initial_user: Optional[str] = None
    value: Optional[str] = None
    style: Optional[ActionStyle] = None
    confirm: Optional[Confirm] = None
    placeholder: Optional[Text] = None
    initial_value: Optional[str] = None

    @staticmethod
    def button(action_id: str, text: str, style: Optional[ActionStyle] = None,
               value: Optional[str] = None, confirm: Optional[Confirm] = None) -> 'Element':
        return Element('button', action_id=action_id, text=Text.plain(text),
                       style=style, value=value, confirm=confirm)

    @staticmethod
    def select(action_id: str, placeholder: str, options: List[Option],
               initial_option: Optional[Option] = None) -> 'Element':
        return Element('static_select', action_id=action_id, placeholder=Text.plain(placeholder),
                       options=options, initial_option=initial_option)

    @staticmethod
    def group_select(action_id: str, placeholder: str, groups: List[OptionGroup],
                     initial_option: Optional[Option] = None) -> 'Element':
        return Element('static_select', action_id=action_id, placeholder=Text.plain(placeholder),
                       option_groups=groups, initial_option=initial_option)

    @staticmethod
    def select_channel(action_id: str, placeholder: str, initial_channel: Optional[str] = None):
        return Element('channels_select', action_id=action_id, placeholder=Text.plain(placeholder),
                       initial_channel=initial_channel)

    @staticmethod
    def select_user(action_id: str, placeholder: str, initial_user: Optional[str] = None):
        return Element('users_select', action_id=action_id, placeholder=Text.plain(placeholder),
                       initial_user=initial_user)

    @staticmethod
    def datepicker(action_id: str, placeholder: str, initial_date: Optional[str] = None):
        return Element('datepicker', action_id=action_id, placeholder=Text.plain(placeholder),
                       initial_date=initial_date)

    @staticmethod
    def input(action_id: str, placeholder: Optional[str] = None, initial_value: Optional[str] = None):
        return Element('plain_text_input', action_id=action_id,
                       placeholder=Text.plain(placeholder) if placeholder else None,
                       initial_value=initial_value)

    @staticmethod
    def radio(action_id: str, options: List[Option], initial_option: Optional[Option] = None):
        return Element('radio_buttons', action_id=action_id, options=options, initial_option=initial_option)


@no_camel_case
@dataclass
class Block:
    type: str
    text: Optional[Text] = None
    elements: List[Union[Text, Element]] = None
    accessory: Optional[Element] = None
    title: Optional[Text] = None
    image_url: Optional[str] = None
    alt_text: Optional[str] = None
    label: Optional[Text] = None
    element: Optional[Element] = None
    block_id: Optional[str] = None
    optional: Optional[bool] = None

    @staticmethod
    def section(text: str, accessory: Optional[Element] = None) -> 'Block':
        return Block('section', text=Text('mrkdwn', text), accessory=accessory)

    @staticmethod
    def actions(*elements: Element) -> 'Block':
        return Block('actions', elements=list(elements))

    @staticmethod
    def divider() -> 'Block':
        return Block('divider')

    @staticmethod
    def context(text: str) -> 'Block':
        return Block('context', elements=[Text.mrkdwn(text)])

    @staticmethod
    def image(title: str, url: str, alt_text: str):
        return Block('image', title=Text.plain(title), image_url=url, alt_text=alt_text)

    @staticmethod
    def input(block_id: str, label: str, element: Element, optional: bool = False) -> 'Block':
        return Block('input', block_id=block_id, label=Text.plain(label), element=element, optional=optional)


@no_camel_case
@dataclass
class View:
    type: str
    callback_id: str
    title: Text
    blocks: List[Block]
    submit: Optional[Text]
    private_metadata: Optional[str]
    notify_on_close: Optional[bool] = False

    @staticmethod
    def modal(callback_id: str, title: str, blocks: Iterable[Block], submit: Optional[str] = None,
              notify_on_close: bool = False, private_metadata: Optional[str] = None) -> 'View':
        submit = Text.plain(submit) if submit else None
        return View('modal', callback_id=callback_id, title=Text.plain(title), blocks=list(blocks), submit=submit,
                    notify_on_close=notify_on_close, private_metadata=private_metadata)


@dataclass
class ViewError:
    block_id: str
    message: str


@no_camel_case
@dataclass
class Message:
    text: Optional[str] = None
    response_type: ResponseType = ResponseType.in_channel
    replace_original: bool = False
    delete_original: bool = False
    blocks: List[Block] = None

    @staticmethod
    def ephemeral(blocks: Iterable[Block]):
        return Message('', blocks=list(blocks), response_type=ResponseType.ephemeral)

    @staticmethod
    def replace(blocks: Iterable[Block]):
        return Message('', blocks=list(blocks), replace_original=True)

    @staticmethod
    def delete():
        return Message(delete_original=True)
