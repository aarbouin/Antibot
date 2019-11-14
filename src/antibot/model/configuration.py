from typing import List


class Configuration:
    def __init__(self, verification_token, oauth_token, vhost, signing_secret: str,
                 ws_api_key: str, ws_ip_restictions: List[str], user_auth_token: str):
        self.verification_token = verification_token
        self.oauth_token = oauth_token
        self.vhost = vhost
        self.signing_secret = signing_secret
        self.ws_api_key = ws_api_key
        self.ws_ip_restictions = ws_ip_restictions
        self.user_auth_token = user_auth_token
