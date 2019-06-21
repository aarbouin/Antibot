from enum import Enum
from typing import Optional, List

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
    def of(value: str) -> 'Option':
        return Option(Text.plain(value), value)


@no_camel_case
class Element:
    def __init__(self, type: str, action_id: str, text: Optional[Text] = None,
                 placeholder: Optional[Text] = None, options: List[Option] = None,
                 initial_option: Optional[Option] = None, initial_date: Optional[str] = None,
                 style: Optional[ActionStyle] = None):
        self.type = type
        self.action_id = action_id
        self.text = text
        self.placeholder = placeholder
        self.options = options
        self.initial_option = initial_option
        self.initial_date = initial_date
        self.style = style

    @staticmethod
    def button(action_id: str, text: str, style: Optional[ActionStyle] = None) -> 'Element':
        return Element('button', action_id=action_id, text=Text.plain(text), style=style)

    @staticmethod
    def select(action_id: str, placeholder: str, options: List[Option],
               initial_option: Optional[Option] = None) -> 'Element':
        return Element('static_select', action_id=action_id, placeholder=Text.plain(placeholder),
                       options=options, initial_option=initial_option)

    @staticmethod
    def datepicker(action_id: str, placeholder: str, initial_date: Optional[str] = None):
        return Element('datepicker', action_id=action_id, placeholder=Text.plain(placeholder),
                       initial_date=initial_date)


@no_camel_case
class Block:
    def __init__(self, type: str, text: Optional[Text] = None, elements: List[Element] = None,
                 accessory: Optional[Element] = None):
        self.type = type
        self.text = text
        self.elements = elements
        self.accessory = accessory

    @staticmethod
    def section(text: str, accessory: Optional[Element] = None) -> 'Block':
        return Block('section', text=Text('mrkdwn', text), accessory=accessory)

    @staticmethod
    def actions(*elements: Element) -> 'Block':
        return Block('actions', elements=list(elements))
