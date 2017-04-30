from antibot.flow.command import BotCommand
from antibot.flow.matchers import find_matchers


def collect_commands(plugins):
    for cls in plugins:
        for matcher, method in find_matchers(cls):
            cmd = BotCommand(cls, method, matcher)
            yield cmd


class PluginsCollection:
    def __init__(self, plugins):
        self.plugins = plugins
        self.commands = list(collect_commands(plugins))
