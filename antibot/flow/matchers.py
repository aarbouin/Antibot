import re
from inspect import getmembers

from antibot.constants import ANTIBOT_MATCHERS
from antibot.domain.message import Message


class Matcher:
    def matches(self, message: Message) -> bool:
        pass


class AndMatcher(Matcher):
    def __init__(self, left_matcher: Matcher, right_matcher: Matcher):
        self.left_matcher = left_matcher
        self.right_matcher = right_matcher

    def matches(self, message: Message):
        message_ = self.left_matcher.matches(message) and self.right_matcher.matches(message)
        return message_


class CommandMatcher(Matcher):
    def __init__(self, command):
        self.command = command

    def matches(self, message: Message):
        return message.body.startswith('!' + self.command)


class RoomMatcher(Matcher):
    def __init__(self, room: str):
        self.room = room

    def matches(self, message: Message):
        return message.room.name == self.room


class UserMatcher(Matcher):
    def __init__(self, name: str):
        self.name = name

    def matches(self, message: Message):
        return message.user.name == self.name


class RegexMatcher(Matcher):
    def __init__(self, pattern):
        self.reg = re.compile(pattern)

    def matches(self, message: Message):
        return self.reg.match(message.body) is not None


class TrueMatcher(Matcher):
    def matches(self, message: Message):
        return True


def find_matchers(cls):
    class_matchers = getattr(cls, ANTIBOT_MATCHERS, TrueMatcher())
    for method in getmembers(cls):
        matcher = getattr(method[1], ANTIBOT_MATCHERS, None)
        if matcher is not None:
            real_matcher = AndMatcher(class_matchers, matcher)
            yield real_matcher, method[1]


def assign_matcher(f, matcher):
    previous_matcher = getattr(f, ANTIBOT_MATCHERS, None)
    if previous_matcher is not None:
        matcher = AndMatcher(matcher, previous_matcher)
    setattr(f, ANTIBOT_MATCHERS, matcher)
