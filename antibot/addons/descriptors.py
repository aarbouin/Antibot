from inspect import getmembers
from typing import List

from antibot.constants import GLANCE_ATTR, PANEL_ATTR, DIALOG_ATTR, WS_ATTR


class WsDescriptor:
    def __init__(self, method: str, route: str, http_method: str):
        self.http_method = http_method
        self.method = method
        self.route = route

    @property
    def id(self):
        return self.method.__name__


def find_wss(cls):
    for name, method in getmembers(cls):
        if hasattr(method, WS_ATTR):
            yield getattr(method, WS_ATTR)


class ActionDescriptor:
    def __init__(self, method: str, name: str):
        self.method = method
        self.name = name

    @property
    def id(self):
        return self.method.__name__


class PanelDescriptor:
    def __init__(self, method: str, name: str):
        self.method = method
        self.name = name

    @property
    def id(self):
        return self.method.__name__


def find_dialogs(cls):
    for name, method in getmembers(cls):
        if hasattr(method, DIALOG_ATTR):
            yield getattr(method, DIALOG_ATTR)


class DialogButton:
    def __init__(self, key: str, text: str):
        self.key = key
        self.text = text


class DialogDescriptor:
    def __init__(self, method: str, title: str, primary: DialogButton = None, secondary: DialogButton = None,
                 width: str = None, height: str = None):
        self.method = method
        self.title = title
        self.primary = primary
        self.secondary = secondary
        self.width = width
        self.height = height

    @property
    def id(self):
        return self.method.__name__


def find_panels(cls):
    for name, method in getmembers(cls):
        if hasattr(method, PANEL_ATTR):
            yield getattr(method, PANEL_ATTR)


class GlanceDescriptor:
    def __init__(self, method, name: str, icon: str):
        self.method = method
        self.name = name
        self.icon = icon

    @property
    def id(self):
        return self.method.__name__


def find_glances(cls):
    for name, method in getmembers(cls):
        if hasattr(method, GLANCE_ATTR):
            yield getattr(method, GLANCE_ATTR)


class AddOnDescriptor:
    def __init__(self, cls, name: str, description: str, glances: List[GlanceDescriptor],
                 panels: List[PanelDescriptor], dialogs: List[DialogDescriptor], wss: List[WsDescriptor]):
        self.cls = cls
        self.name = name
        self.description = description
        self.glances = glances
        self.panels = panels
        self.dialogs = dialogs
        self.wss = wss

    @property
    def id(self):
        return self.cls.__name__

    def db_key(self, room_id):
        return '{}-{}'.format(self.id, room_id)
