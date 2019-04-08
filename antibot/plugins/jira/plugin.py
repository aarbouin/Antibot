from bottle import request
from pyckson import parse
from pynject import pynject

from antibot.decorators import ws
from antibot.model.plugin import AntibotPlugin
from antibot.plugins.jira.errors import ErrorsRepository
from antibot.plugins.jira.model import JiraEvent
from antibot.repository.users import UsersRepository
from antibot.slack.api import SlackApi
from antibot.slack.message import Message, Attachment


@pynject
class Jira(AntibotPlugin):
    def __init__(self, api: SlackApi, users: UsersRepository, errors: ErrorsRepository):
        super().__init__('Jira')
        self.api = api
        self.users = users
        self.errors = errors

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

        url = 'https://jira.antidot.net/browse/' + event.issue.key
        if len(problems) > 0:
            count = self.errors.get_and_inc(user)

            problems = ' and '.join(problems)
            msg_template = '<@{}> <{}|{}> was moved to done but {}'
            message = msg_template.format(user.id, url, event.issue.key, problems)

            suf = lambda n: "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th"))
            attachment_text = 'This is the {} time this month {}'.format(suf(count), self.smiley(count))
            attachment = Attachment('void', text=attachment_text)
            self.api.post_message('ft-product-team', Message(text=message, attachments=[attachment]))
        else:
            msg_template = '<{}|{}> was move to done by <@{}>'
            message = msg_template.format(url, event.issue.key, user.id)
            attachments = []
            rn_attachment = '{}'.format(event.issue.fields.release_note)
            color = '#ff0a0a' if event.issue.fields.issuetype.name == 'Bug' else '#7acc00'
            attachments.append(Attachment('void', text=rn_attachment, color=color))
            if event.issue.fields.upgrade_information.strip() not in ['', 'None']:
                ui_attachment = 'Upgrade Information : {}'.format(event.issue.fields.upgrade_information)
                attachments.append(Attachment('void', text=ui_attachment, color='#2196f3'))
            self.api.post_message('ft-product-team', Message(text=message, attachments=attachments))

    def smiley(self, count) -> str:
        if count <= 1:
            return ':wink:'
        if count < 5:
            return ':white_frowning_face:'
        return ':angry:'
