from enum import Enum
from typing import Optional, List, Union, Iterable

from pyckson import no_camel_case


class ActionStyle(Enum):
    default = 'default'
    primary = 'primary'
    danger = 'danger'


@no_camel_case
class Text:
    def __init__(self, type: str, text: str):
        self.type = type
        self.text = text

    @staticmethod
    def mrkdwn(text: str) -> 'Text':
        return Text('mrkdwn', text)

    @staticmethod
    def plain(text: str) -> 'Text':
        return Text('plain_text', text)


@no_camel_case
class Option:
    def __init__(self, text: Text, value: str):
        self.text = text
        self.value = value

    @staticmethod
    def of(value: str, text: Optional[str] = None) -> 'Option':
        text = text or value
        return Option(Text.plain(text), value)


@no_camel_case
class Confirm:
    def __init__(self, title: Text, text: Text, confirm: Text, deny: Text):
        self.title = title
        self.text = text
        self.confirm = confirm
        self.deny = deny

    @staticmethod
    def of(title: str, text: str, confirm: str, deny: str) -> 'Confirm':
        return Confirm(Text.plain(title), Text.mrkdwn(text),
                       Text.plain(confirm), Text.plain(deny))


@no_camel_case
class Element:
    def __init__(self, type: str, action_id: str, text: Optional[Text] = None,
                 placeholder: Optional[Text] = None, options: List[Option] = None,
                 initial_option: Optional[Option] = None, initial_date: Optional[str] = None,
                 style: Optional[ActionStyle] = None, value: Optional[str] = None,
                 initial_channel: Optional[str] = None, initial_user: Optional[str] = None,
                 confirm: Optional[Confirm] = None, initial_value: Optional[str] = None):
        self.type = type
        self.action_id = action_id
        self.text = text
        self.placeholder = placeholder
        self.options = options
        self.initial_option = initial_option
        self.initial_date = initial_date
        self.style = style
        self.value = value
        self.initial_channel = initial_channel
        self.initial_user = initial_user
        self.confirm = confirm
        self.initial_value = initial_value

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
    def text(action_id: str, placeholder: str, initial_value: Optional[str] = None):
        return Element('plain_text_input', action_id=action_id, placeholder=Text.plain(placeholder),
                       initial_value=initial_value)


@no_camel_case
class Block:
    def __init__(self, type: str, text: Optional[Text] = None, elements: List[Union[Text, Element]] = None,
                 accessory: Optional[Element] = None, title: Optional[Text] = None, image_url: Optional[str] = None,
                 alt_text: Optional[str] = None, label: Optional[Text] = None, element: Optional[Element] = None,
                 block_id: Optional[str] = None):
        self.type = type
        self.text = text
        self.elements = elements
        self.accessory = accessory
        self.title = title
        self.image_url = image_url
        self.alt_text = alt_text
        self.label = label
        self.element = element
        self.block_id = block_id

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
    def input(block_id: str, label: str, element: Element) -> 'Block':
        return Block('input', block_id=block_id, label=Text.plain(label), element=element)


@no_camel_case
class View:
    def __init__(self, type: str, callback_id: str, title: Text, blocks: List[Block], submit: Optional[Text] = None,
                 notify_on_close: bool = False, private_metadata: Optional[str] = None):
        self.type = type
        self.callback_id = callback_id
        self.title = title
        self.blocks = blocks
        self.submit = submit
        self.notify_on_close = notify_on_close
        self.private_metadata = private_metadata

    @staticmethod
    def modal(callback_id: str, title: str, blocks: Iterable[Block], submit: Optional[str] = None,
              notify_on_close: bool = False, private_metadata: Optional[str] = None) -> 'View':
        submit = Text.plain(submit) if submit else None
        return View('modal', callback_id=callback_id, title=Text.plain(title), blocks=list(blocks), submit=submit,
                    notify_on_close=notify_on_close, private_metadata=private_metadata)
