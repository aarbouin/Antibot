from inspect import signature

from antibot.addons.descriptor import CommandDescriptor
from antibot.constants import METHOD_HAS_USER_ATTR, METHOD_HAS_ROOM_ATTR, CMD_ATTR, JOB_ATTR_DAILY


def set_params_options(f):
    for name, param in signature(f).parameters.items():
        if name == 'user':
            setattr(f, METHOD_HAS_USER_ATTR, True)
        if name == 'room':
            setattr(f, METHOD_HAS_ROOM_ATTR, True)


def command(route):
    def decorator(f):
        setattr(f, CMD_ATTR, CommandDescriptor(route, f))
        set_params_options(f)
        return f

    return decorator


def daily(hour='00:00'):
    def decorator(f):
        setattr(f, JOB_ATTR_DAILY, hour)
        return f

    return decorator
