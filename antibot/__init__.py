from antibot.client import HipchatClient
from antibot.decorators import addon, glance, botcmd
from antibot.domain.glance import GlanceView, GlanceStatus, GlanceStatusColor
from antibot.domain.message import Message
from antibot.domain.plugin import AntibotPlugin

__version__ = '0.1'
__all__ = ['HipchatClient', 'AntibotPlugin',
           'Message',
           'addon', 'glance', 'GlanceView', 'GlanceStatus', 'GlanceStatusColor', 'botcmd']
