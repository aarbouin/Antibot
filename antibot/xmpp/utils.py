import re


class JID:
    def __init__(self, jid: str):
        self.jid = jid
        parts = re.match('([0-9]+)_([0-9]+)@(.+)', jid)
        if parts is None:
            raise ValueError('Invalid JID : {}'.format(jid))
        self.base = parts.group(0)
        self.api_id = parts.group(1)
        self.domain = parts.group(2)

    @staticmethod
    def build(base, api_id, domain) -> str:
        return '{}_{}@{}'.format(base, api_id, domain)
