from typing import Type

from pyckson import serialize
from pynject import Injector, pynject

from antibot.model.plugin import AntibotPlugin


@pynject
class WsRunner:
    def __init__(self, injector: Injector):
        self.injector = injector

    def run_ws(self, method, plugin: Type[AntibotPlugin], **kwargs):
        instance = self.injector.get_instance(plugin)

        reply = method(instance, **kwargs)
        if reply is not None:
            if isinstance(reply, dict):
                return reply
            else:
                return serialize(reply)
