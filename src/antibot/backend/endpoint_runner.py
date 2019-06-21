from inspect import signature
from typing import Type, Callable

from pynject import pynject, Injector


@pynject
class EndpointRunner:
    def __init__(self, injector: Injector):
        self.injector = injector

    def run(self, plugin: Type, method: Callable, **kwargs):
        instance = self.injector.get_instance(plugin)
        method_args = {}

        for name, param in signature(method).parameters.items():
            if name in kwargs:
                method_args[name] = kwargs[name]

        return method(instance, **method_args)
