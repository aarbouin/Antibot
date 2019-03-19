import os
import re
from json import loads
from typing import List

import requests
from bottle import request
from pyckson import parse
from pynject import pynject
from requests.auth import HTTPBasicAuth

from antibot.decorators import event_callback
from antibot.decorators import ws
from antibot.model.plugin import AntibotPlugin
from antibot.plugins.jira.errors import ErrorsRepository
from antibot.plugins.jira.model import JiraEvent
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.event import EventType, MessageEvent
from antibot.slack.message import Field
from antibot.slack.message import Message, Attachment


@pynject
class Jira(AntibotPlugin):
    def __init__(self, api: SlackApi, users: UsersRepository, errors: ErrorsRepository):
        super().__init__('Jira')
        self.jira_home = os.environ.get('JIRA_HOME', '')
        jira_login = os.environ.get('JIRA_LOGIN', '')
        jira_password = os.environ.get('JIRA_PASSWORD', '')
        self.auth = HTTPBasicAuth(jira_login, jira_password)
        self.api = api
        self.users = users
        self.errors = errors

    @event_callback(EventType.message)
    def link_issues(self, event: MessageEvent):
        if event.bot_id is not None:
            return
        if not event.text or not self.jira_home:
            return
        found_issues = self._find_jira_issues(event)
        if found_issues:
            attachments = [self._to_attachment(i) for i in found_issues]
            self.api.update_message(event.channel, event.ts, Message(text=event.text, attachments=attachments))

    def _find_jira_issues(self, event: MessageEvent) -> List[dict]:
        found_issues = []
        maybe_issues = set(re.findall(r'[A-Z0-9]{2,}-[0-9]+', event.text))
        for issue in maybe_issues:
            response = requests.get('{}/rest/api/latest/issue/{}'.format(self.jira_home, issue), auth=self.auth)
            if response.status_code == 200:
                found_issues.append(loads(response.text))
        return found_issues

    def _to_attachment(self, issue: dict) -> Attachment:
        key = issue.get('key', '')
        fields = issue.get('fields', {})
        issuetype = fields.get('issuetype', {}).get('name', '')
        status = fields.get('status', {}).get('name', '')
        return Attachment(title='[{}] {}'.format(key, fields.get('summary', '')),
                          title_link='{}/browse/{}'.format(self.jira_home, key),
                          text=fields.get('description', ''),
                          color='#0747a6',
                          fields=[Field(issuetype, short=True), Field(status, short=True)])

    @ws('/jira/validate', method='POST')
    def jira_hook(self):
        event = parse(JiraEvent, request.json)
        user = self.users.get_by_email(event.user.email_address)

        if 'not-for-release-note' in event.issue.fields.labels:
            return

        if event.issue.fields.issuetype.name in ['Task', 'Think']:
            return

        problems = []
        if event.issue.fields.release_note == 'None' or len(event.issue.fields.release_note.strip()) == 0:
            problems.append('has no release note information')

        if len(event.issue.fields.fix_versions) == 0:
            problems.append('has no release version')

        if len(problems) > 0:
            count = self.errors.get_and_inc(user)

            url = 'https://jira.antidot.net/browse/' + event.issue.key
            problems = ' and '.join(problems)
            msg_template = '<@{}> <{}|{}> was moved to done but {}'
            message = msg_template.format(user.id, url, event.issue.key, problems)

            suf = lambda n: "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th"))
            attachment_text = 'This is the {} time this month {}'.format(suf(count), self.smiley(count))
            attachment = Attachment('test', text=attachment_text)
            self.api.post_message('ft-product-team', Message(text=message, attachments=[attachment]))

    def smiley(self, count) -> str:
        if count <= 1:
            return ':wink:'
        if count < 5:
            return ':white_frowning_face:'
        return ':angry:'
