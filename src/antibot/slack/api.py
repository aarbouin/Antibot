from typing import Iterator

from pyckson import parse, serialize
from pynject import singleton, pynject
from slack import WebClient

from antibot.model.configuration import Configuration
from antibot.model.user import User
from antibot.slack.channel import Channel
from antibot.slack.message import Message
from antibot.slack.user import Member


@pynject
class SlackClientProvider:
    def __init__(self, configuration: Configuration):
        self.configuration = configuration

    def get(self) -> WebClient:
        return WebClient(self.configuration.oauth_token)


@singleton
@pynject
class SlackApi:
    def __init__(self, client: WebClient):
        self.client = client

    def list_users(self) -> Iterator[User]:
        result = self.client.api_call('users.list')
        for member in result['members']:
            member = parse(Member, member)
            yield User(member.id, member.profile.display_name, member.profile.email)

    def get_channel(self, channel_id) -> Channel:
        result = self.client.channels_info(channel=channel_id)
        channel = parse(Channel, result['channel'])
        return channel

    def post_message(self, channel_id: str, message: Message) -> str:
        attachments = [serialize(att) for att in message.attachments] if message.attachments is not None else None
        result = self.client.chat_postMessage(channel=channel_id, text=message.text,
                                              attachments=attachments)
        return result['ts']

    def get_permalink(self, channel_id: str, timestamp: str) -> str:
        result = self.client.chat_getPermalink(channel=channel_id, message_ts=timestamp)
        return result['permalink']

    def update_message(self, channel_id: str, timestamp: str, message: Message) -> str:
        attachments = [serialize(att) for att in message.attachments] if message.attachments is not None else None
        result = self.client.chat_update(channel=channel_id, ts=timestamp,
                                         text=message.text, attachments=attachments)
        return result['ts']
