from typing import Iterator

from pyckson import parse
from pynject import singleton, pynject
from slackclient import SlackClient

from antibot.model.configuration import Configuration
from antibot.model.user import User
from antibot.slack.channel import Channel
from antibot.slack.message import Message
from antibot.slack.user import Member


@pynject
class SlackClientProvider:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def get(self) -> SlackClient:
        return SlackClient(self.configuration.oauth_token)


@singleton
@pynject
class SlackApi:
    def __init__(self, client: SlackClient):
        self.client = client

    def list_users(self) -> Iterator[User]:
        result = self.client.api_call('users.list')
        for member in result['members']:
            member = parse(Member, member)
            yield User(member.id, member.profile.display_name)

    def get_channel(self, channel_id) -> Channel:
        result = self.client.api_call('channels.info', channel=channel_id)
        channel = parse(Channel, result['channel'])
        return channel

    def post_message(self, channel_id: str, text: str) -> str:
        result = self.client.api_call('chat.postMessage', channel=channel_id, text=text)
        return result['ts']

    def get_permalink(self, channel_id: str, timestamp: str) -> str:
        result = self.client.api_call('chat.getPermalink', channel=channel_id, message_ts=timestamp)
        return result['permalink']

    def update_message(self, channel_id: str, timestamp: str, message: Message) -> str:
        result = self.client.api_call('chat.update', channel=channel_id, ts=timestamp,
                                      text=message.text, attachments=message.attachments)
        return result['ts']
