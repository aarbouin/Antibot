import hashlib
import hmac
import time

from bottle import BaseRequest, abort
from pynject import pynject

from antibot.model.configuration import Configuration


@pynject
class RequestChecker:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def check_request(self, request: BaseRequest):
        timestamp = request.headers['X-Slack-Request-Timestamp ']
        if abs(time.time() - float(timestamp)) > 60 * 5:
            abort(401, 'Invalid timestamp')
        body = request.body.read()
        data = 'v0:{}:'.format(timestamp).encode() + body
        request_hash = 'v0=' + hmac.new(str.encode(self.configuration.signing_secret),
                                        data, hashlib.sha256).hexdigest()
        signature = request.headers['X-Slack-Signature']
        if not hmac.compare_digest(request_hash, signature):
            abort(401)
