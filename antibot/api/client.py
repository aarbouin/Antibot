from slackclient import SlackClient


class SlackApi:
    def __init__(self, client: SlackClient):
        self.client = client
