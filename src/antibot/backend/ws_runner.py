import traceback
from typing import Type

from bottle import request, abort, HTTPError
from pyckson import serialize
from pynject import Injector, pynject

from antibot.backend.constants import WS_JSON_VALUES
from antibot.model.configuration import Configuration
from antibot.model.plugin import AntibotPlugin


@pynject
class WsRunner:
    def __init__(self, injector: Injector, configuration: Configuration):
        self.injector = injector
        self.configuration = configuration

    def run_ws(self, method, plugin: Type[AntibotPlugin], **kwargs):
        if self.configuration.ws_api_key != request.params.get('apikey'):
            abort(401, 'Could not verify api key')
        ip = request.get_header('X-Forwarded-For', request.environ.get('REMOTE_ADDR'))
        if len(self.configuration.ws_ip_restictions) > 0 and ip not in self.configuration.ws_ip_restictions:
            abort(401, 'Unauthorized IP')
        instance = self.injector.get_instance(plugin)

        try:
            reply = method(instance, **kwargs)
            if reply is not None:
                if getattr(method, WS_JSON_VALUES, False):
                    return serialize(reply)
                return reply
        except Exception as e:
            if not isinstance(e, HTTPError):
                traceback.print_exc()
                abort(500)
