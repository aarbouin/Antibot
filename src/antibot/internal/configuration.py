from dataclasses import dataclass


@dataclass
class Configuration:
    verification_token: str
    oauth_token: str
    vhost: str
    signing_secret: str
    ws_api_key: str
    user_auth_token: str
    prod: bool
