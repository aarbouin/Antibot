from antibot.constants import METHOD_HAS_USER_ATTR, METHOD_HAS_ROOM_ATTR
from antibot.domain.room import Room
from antibot.domain.user import User


def addon_method_runner(method, instance, user: User, room: Room, kwargs = None):
    kwargs = kwargs or {}
    if getattr(method, METHOD_HAS_USER_ATTR, False):
        kwargs['user'] = user
    if getattr(method, METHOD_HAS_ROOM_ATTR, False):
        kwargs['room'] = room
    return method(instance, **kwargs)
