class Configuration:
    def __init__(self, verification_token, oauth_token, vhost, signing_secret: str):
        self.verification_token = verification_token
        self.oauth_token = oauth_token
        self.vhost = vhost
        self.signing_secret = signing_secret
