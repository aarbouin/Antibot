from functools import wraps

import schedule

from antibot.addons.descriptors import find_glances, AddOnDescriptor, GlanceDescriptor, PanelDescriptor, find_panels
from antibot.constants import GLANCE_ATTR, ADDON_ATTR, PANEL_ATTR, JOB_ATTR
from antibot.domain.message import Message
from antibot.flow.matchers import assign_matcher, CommandMatcher, RoomMatcher, RegexMatcher


def botcmd(cmd):
    def decorator(f):
        matcher = CommandMatcher(cmd)
        assign_matcher(f, matcher)
        return f

    return decorator


def hear(pattern):
    def decorator(f):
        matcher = RegexMatcher(pattern)
        assign_matcher(f, matcher)

        @wraps(f)
        def wrapper(self, message: Message):
            match = matcher.reg.match(message.body)
            f(self, message, **match.groupdict())

        return wrapper

    return decorator


def room(name):
    def decorator(f_or_cls):
        assign_matcher(f_or_cls, RoomMatcher(name))
        return f_or_cls

    return decorator


def addon(name, description):
    def decorator(cls):
        glances = list(find_glances(cls))
        panels = list(find_panels(cls))
        descriptor = AddOnDescriptor(cls, name, description, list(glances), list(panels))
        for glance in glances:
            setattr(glance.method, ADDON_ATTR, descriptor)
        for panel in panels:
            setattr(panel.method, ADDON_ATTR, descriptor)
        setattr(cls, ADDON_ATTR, descriptor)
        return cls

    return decorator


def glance(name, icon):
    def decorator(f):
        setattr(f, GLANCE_ATTR, GlanceDescriptor(f, name, icon))
        return f

    return decorator


def panel(name):
    def decorator(f):
        setattr(f, PANEL_ATTR, PanelDescriptor(f, name))
        return f

    return decorator


def daily(hour='00:00'):
    def decorator(f):
        job = schedule.every().day.at(hour)
        setattr(f, JOB_ATTR, job)
        return f

    return decorator
