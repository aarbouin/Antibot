from typing import List


class Configuration:
    def __init__(self, jid: str, password: str, base_url: str, static_dir: str, plugins_package: str,
                 rooms_to_join: List[str], api_token: str):
        self.jid = jid
        self.password = password
        self.base_url = base_url
        self.static_dir = static_dir
        self.plugins_package = plugins_package
        self.rooms_to_join = rooms_to_join
        self.api_token = api_token
