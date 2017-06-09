from enum import Enum


class GlanceColor(Enum):
    default = 1
    success = 2
    error = 3
    current = 4
    complete = 6
    moved = 7


class GlanceStatus:
    def __init__(self, color: GlanceColor, text: str):
        self.color = color
        self.text = text


class GlanceView:
    def __init__(self, text: str, status: GlanceStatus = None):
        self.text = text
        self.status = status
