from dataclasses import dataclass


@dataclass
class Configuration:
    bot_user_oauth_token: str
    signing_secret: str
    ws_api_key: str
    vhost: str
    prod: bool
