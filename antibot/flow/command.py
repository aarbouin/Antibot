from pynject import pynject, Injector

from antibot.domain.message import Message
from antibot.flow.matchers import Matcher


class BotCommand:
    def __init__(self, cls, method, matcher: Matcher):
        self.cls = cls
        self.method = method
        self.matcher = matcher

    def matches(self, message: Message) -> bool:
        return self.matcher.matches(message)


@pynject
class CommandRunner:
    def __init__(self, injector: Injector):
        self.injector = injector

    def run_command(self, cmd: BotCommand, message: Message):
        instance = self.injector.get_instance(cmd.cls)
        cmd.method(instance, message)
