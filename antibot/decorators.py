from functools import wraps
from inspect import signature
from typing import Tuple

import schedule

from antibot.addons.descriptors import find_glances, AddOnDescriptor, GlanceDescriptor, PanelDescriptor, find_panels, \
    DialogDescriptor, find_dialogs, DialogButton, WsDescriptor, find_wss, ButtonPos, ActionDescriptor
from antibot.constants import GLANCE_ATTR, ADDON_ATTR, PANEL_ATTR, JOB_ATTR, DIALOG_ATTR, ACTION_ATTR, WS_ATTR, \
    METHOD_HAS_USER_ATTR, METHOD_HAS_ROOM_ATTR, SECONDARY_BUTTONS_ATTR, PRIMARY_BUTTON_ATTR
from antibot.domain.message import Message
from antibot.flow.matchers import assign_matcher, CommandMatcher, RoomMatcher, RegexMatcher


def set_params_options(f):
    for name, param in signature(f).parameters.items():
        if name == 'user':
            setattr(f, METHOD_HAS_USER_ATTR, True)
        if name == 'room':
            setattr(f, METHOD_HAS_ROOM_ATTR, True)


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
        dialogs = list(find_dialogs(cls))
        wss = list(find_wss(cls))
        descriptor = AddOnDescriptor(cls, name, description, list(glances), list(panels), list(dialogs), list(wss))
        for glance in glances:
            setattr(glance.method, ADDON_ATTR, descriptor)
        for panel in panels:
            setattr(panel.method, ADDON_ATTR, descriptor)
        for dialog in dialogs:
            setattr(dialog.method, ADDON_ATTR, descriptor)
        for ws in wss:
            setattr(ws.method, ADDON_ATTR, descriptor)
        setattr(cls, ADDON_ATTR, descriptor)
        return cls

    return decorator


def ws(route: str, method: str = 'GET'):
    def decorator(f):
        setattr(f, WS_ATTR, WsDescriptor(f, route, method))
        set_params_options(f)
        return f

    return decorator


def glance(name, icon):
    def decorator(f):
        setattr(f, GLANCE_ATTR, GlanceDescriptor(f, name, icon))
        set_params_options(f)
        return f

    return decorator


def panel(name):
    def decorator(f):
        setattr(f, PANEL_ATTR, PanelDescriptor(f, name))
        set_params_options(f)
        return f

    return decorator


def dialog(title: str, size: Tuple[str, str] = None):
    def decorator(f):
        width, height = (size[0], size[1]) if size else (None, None)
        primary = getattr(f, PRIMARY_BUTTON_ATTR, None)
        secondary = getattr(f, SECONDARY_BUTTONS_ATTR, [])
        descriptor = DialogDescriptor(f, title, width=width, height=height, primary=primary, secondary=secondary)
        setattr(f, DIALOG_ATTR, descriptor)
        set_params_options(f)
        return f

    return decorator


def button(position: ButtonPos, key: str, text: str):
    button = DialogButton(key, text)

    def decorator(f):
        if position == ButtonPos.SECONDARY:
            buttons = getattr(f, SECONDARY_BUTTONS_ATTR, [])
            buttons.append(button)
            setattr(f, SECONDARY_BUTTONS_ATTR, buttons)
        if position == ButtonPos.PRIMARY:
            setattr(f, PRIMARY_BUTTON_ATTR, button)
        return f

    return decorator


def message_action(name):
    def decorator(f):
        setattr(f, ACTION_ATTR, ActionDescriptor(f, name))
        return f

    return decorator


def daily(hour='00:00'):
    def decorator(f):
        job = schedule.every().day.at(hour)
        setattr(f, JOB_ATTR, job)
        return f

    return decorator
