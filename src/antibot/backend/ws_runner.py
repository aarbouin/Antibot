import traceback
from typing import Type

from bottle import request, abort, HTTPError
from pyckson import serialize
from pynject import Injector, pynject

from antibot.backend.constants import WS_JSON_VALUES
from antibot.model.configuration import Configuration
from antibot.model.plugin import AntibotPlugin
from antibot.slack.api import SlackApi
from antibot.tools import notify_errors


@pynject
class WsRunner:
    def __init__(self, injector: Injector, configuration: Configuration, api: SlackApi):
        self.injector = injector
        self.configuration = configuration
        self.api = api

    def run_ws(self, method, plugin: Type[AntibotPlugin], **kwargs):
        request_key = request.params.get('apikey') or request.headers.get('X-Gitlab-Token')
        if self.configuration.ws_api_key != request_key:
            abort(401, 'Could not verify api key')
        ip = request.get_header('X-Forwarded-For', request.environ.get('REMOTE_ADDR'))
        if len(self.configuration.ws_ip_restictions) > 0 and ip not in self.configuration.ws_ip_restictions:
            abort(401, 'Unauthorized IP')
        instance = self.injector.get_instance(plugin)

        with notify_errors(self.api, request.json):
            reply = method(instance, **kwargs)
            if reply is not None:
                if getattr(method, WS_JSON_VALUES, False):
                    return serialize(reply)
                return reply
