from typing import List

from pyckson import rename


class JiraUser:
    def __init__(self, name: str, email_address: str):
        self.name = name
        self.email_address = email_address


class JiraVersion:
    def __init__(self, name: str):
        self.name = name


class JiraIssueType:
    def __init__(self, name: str):
        self.name = name


@rename(release_note='customfield_10102')
@rename(upgrade_information='customfield_10800')
class JiraFields:
    def __init__(self, assignee: JiraUser, release_note: str, labels: List[str], fix_versions: List[JiraVersion],
                 issuetype: JiraIssueType, upgrade_information: str):
        self.assignee = assignee
        self.release_note = release_note
        self.labels = labels
        self.fix_versions = fix_versions
        self.issuetype = issuetype
        self.upgrade_information = upgrade_information


class JiraIssue:
    def __init__(self, key: str, fields: JiraFields):
        self.key = key
        self.fields = fields


class JiraEvent:
    def __init__(self, issue: JiraIssue, user: JiraUser):
        self.issue = issue
        self.user = user
