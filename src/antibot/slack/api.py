import logging
from io import BytesIO
from typing import Iterator

import requests
from injector import inject, singleton
from pyckson import parse, serialize, dumps
from requests import HTTPError
from slack import WebClient
from slack.errors import SlackApiError

from antibot.internal.slack.channel import Channel
from antibot.internal.slack.upload import File
from antibot.internal.slack.user import Member
from antibot.slack.message import Message, PostMessageReply, View
from antibot.user import User


@singleton
class SlackApi:
    @inject
    def __init__(self, client: WebClient):
        self.client = client

    def list_users(self) -> Iterator[User]:
        result = self.client.api_call('users.list')
        for member in result['members']:
            member = parse(Member, member)
            name = member.profile.display_name or member.profile.real_name
            yield User(member.id, name, member.profile.email)

    def get_channel(self, channel_id) -> Channel:
        result = self.client.channels_info(channel=channel_id)
        channel = parse(Channel, result['channel'])
        return channel

    def post_message(self, channel_id: str, message: Message) -> PostMessageReply:
        blocks = [serialize(block) for block in message.blocks] if message.blocks is not None else None
        try:
            result = self.client.chat_postMessage(channel=channel_id, text=message.text, blocks=blocks)
            return PostMessageReply(result['channel'], result['message_ts'])
        except SlackApiError as e:
            if e.response['error'] == 'not_in_channel':
                self.client.conversations_join(channel=channel_id)
                result = self.client.chat_postMessage(channel=channel_id, text=message.text, blocks=blocks)
                return PostMessageReply(result['channel'], result['message_ts'])
            else:
                raise e

    def post_ephemeral(self, channel_id: str, user_id: str, message: Message) -> PostMessageReply:
        blocks = [serialize(block) for block in message.blocks] if message.blocks is not None else None
        try:
            result = self.client.chat_postEphemeral(channel=channel_id, user=user_id, text=message.text, blocks=blocks)
            print(result)
            return PostMessageReply(result['channel'], result['message_ts'])
        except SlackApiError as e:
            if e.response['error'] == 'not_in_channel':
                self.client.conversations_join(channel=channel_id)
                result = self.client.chat_postEphemeral(channel=channel_id, user=user_id, text=message.text,
                                                        blocks=blocks)
                return PostMessageReply(result['channel'], result['message_ts'])
            else:
                raise e

    def update_message(self, channel_id: str, timestamp: str, message: Message) -> PostMessageReply:
        blocks = [serialize(block) for block in message.blocks] if message.blocks is not None else None
        result = self.client.chat_update(channel=channel_id, ts=timestamp,
                                         text=message.text, blocks=blocks)
        return PostMessageReply(result['channel'], result['message_ts'])

    def respond(self, response_url: str, message: Message):
        reply = requests.post(response_url, json=serialize(message))
        try:
            reply.raise_for_status()
        except HTTPError:
            logging.getLogger(__name__).error(reply.text)
            print('##### blocks #####')
            print(dumps(message.blocks))
            raise

    def upload_file(self, channel_id: str, filename: str, title: str, content: bytes):
        result = self.client.files_upload(file=BytesIO(content), filename=filename,
                                          title=title, channels=channel_id)
        print(result.data)
        return parse(File, result.data['file'])

    def upload_and_share(self, content: bytes, filename) -> File:
        result = self.user_client.files_upload(file=BytesIO(content), filename=filename)
        result = self.user_client.files_sharedPublicURL(file=result['file']['id'])
        print(result.data)
        return parse(File, result.data['file'])

    def open_modal(self, trigger_id: str, view: View) -> str:
        result = self.client.views_open(trigger_id=trigger_id, view=serialize(view))
        return result['view']['id']

    def push_modal(self, trigger_id: str, view: View) -> str:
        result = self.client.views_push(trigger_id=trigger_id, view=serialize(view))
        return result['view']['id']

    def update_view(self, parent_view_id: str, view: View) -> str:
        result = self.client.views_update(view_id=parent_view_id, view=serialize(view))
        return result['view']['id']
