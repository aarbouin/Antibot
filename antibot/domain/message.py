from enum import Enum

from pyckson import no_camel_case


class MessageType(Enum):
    in_channel = 'in_channel'
    ephemeral = 'ephemeral'


@no_camel_case
class Message:
    def __init__(self, text: str, response_type: MessageType):
        self.text = text
        self.response_type = response_type
