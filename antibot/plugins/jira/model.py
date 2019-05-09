from typing import List, Optional

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


class JiraPriority:
    Blocker = '1'
    Medium = '3'
    OnFire = '10100'

    def __init__(self, name: str, id: str):
        self.name = name
        self.id = id


class JiraProject:
    def __init__(self, id: str, key: str, name: str):
        self.id = id
        self.key = key
        self.name = name


@rename(release_note='customfield_10102')
@rename(upgrade_information='customfield_10800')
class JiraFields:
    def __init__(self, summary: str, labels: List[str], fix_versions: List[JiraVersion],
                 issuetype: JiraIssueType, priority: JiraPriority,
                 assignee: Optional[JiraUser] = None, release_note: Optional[str] = None,
                 upgrade_information: Optional[str] = None, project: Optional[JiraProject] = None):
        self.assignee = assignee
        self.release_note = release_note
        self.labels = labels
        self.fix_versions = fix_versions
        self.issuetype = issuetype
        self.upgrade_information = upgrade_information
        self.priority = priority
        self.project = project
        self.summary = summary


class JiraIssue:
    def __init__(self, key: str, fields: JiraFields):
        self.key = key
        self.fields = fields


class JiraEvent:
    def __init__(self, issue: JiraIssue, user: JiraUser):
        self.issue = issue
        self.user = user
