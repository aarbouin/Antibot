from inspect import signature
from threading import Thread
from typing import Type, Callable

from pyckson import loads
from pynject import pynject, Injector

from antibot.backend.constants import ASYNC_REPLY
from antibot.backend.debugger import Debugger


@pynject
class EndpointRunner:
    def __init__(self, injector: Injector, debugger: Debugger):
        self.injector = injector
        self.debugger = debugger

    def run(self, plugin: Type, method: Callable, **kwargs):
        instance = self.injector.get_instance(plugin)
        method_args = {}

        for name, param in signature(method).parameters.items():
            if name in kwargs:
                if param.annotation != str and type(kwargs[name]) is str:
                    kwargs[name] = loads(param.annotation, kwargs[name])
                method_args[name] = kwargs[name]

        if getattr(method, ASYNC_REPLY, False):
            def runner(r_method, r_instance, r_args):
                with self.debugger.wrap(method_args):
                    r_method(r_instance, **r_args)

            t = Thread(target=runner, args=[method, instance, method_args])
            t.start()
            return
        return method(instance, **method_args)
