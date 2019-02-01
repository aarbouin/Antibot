from inspect import signature

from antibot.backend.constants import EVENT_CALLBACK_ATTR, METHOD_HAS_EVENT_ATTR
from antibot.backend.constants import METHOD_HAS_USER_ATTR, METHOD_HAS_ROOM_ATTR, CMD_ATTR, JOB_ATTR_DAILY, \
    CALLBACK_ATTR, METHOD_HAS_CALLBACK_ID_ATTR, METHOD_HAS_ACTIONS_ATTR, METHOD_HAS_CHANNEL_ATTR, WS_ATTR
from antibot.backend.descriptor import CommandDescriptor, CallbackDescriptor, WsDescriptor
from antibot.backend.descriptor import EventCallbackDescriptor
from antibot.slack.event import EventType


def set_params_options(f):
    for name, param in signature(f).parameters.items():
        if name == 'user':
            setattr(f, METHOD_HAS_USER_ATTR, True)
        if name == 'room':
            setattr(f, METHOD_HAS_ROOM_ATTR, True)
        if name == 'callback_id':
            setattr(f, METHOD_HAS_CALLBACK_ID_ATTR, True)
        if name == 'actions':
            setattr(f, METHOD_HAS_ACTIONS_ATTR, True)
        if name == 'channel':
            setattr(f, METHOD_HAS_CHANNEL_ATTR, True)
        if name == 'event':
            setattr(f, METHOD_HAS_EVENT_ATTR, True)


def command(route):
    def decorator(f):
        setattr(f, CMD_ATTR, CommandDescriptor(route, f))
        set_params_options(f)
        return f

    return decorator


def callback(id_regex):
    def decorator(f):
        setattr(f, CALLBACK_ATTR, CallbackDescriptor(id_regex, f))
        set_params_options(f)
        return f

    return decorator


def ws(route, method='POST'):
    def decorator(f):
        setattr(f, WS_ATTR, WsDescriptor(route, method, f))
        return f

    return decorator


def daily(hour='00:00'):
    def decorator(f):
        setattr(f, JOB_ATTR_DAILY, hour)
        return f

    return decorator


def event_callback(event_type: EventType):
    def decorator(f):
        setattr(f, EVENT_CALLBACK_ATTR, EventCallbackDescriptor(event_type, f))
        set_params_options(f)
        return f

    return decorator
