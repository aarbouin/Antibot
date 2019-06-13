from pynject import pynject

from antibot.decorators import ws
from antibot.model.plugin import AntibotPlugin


@pynject
class BasePlugin(AntibotPlugin):
    def __init__(self):
        super().__init__('Base')

    @ws('/', method='GET')
    def hello(self):
        return 'it\'s working'
