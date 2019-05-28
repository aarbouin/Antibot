import os

from jira import JIRA


class JiraProvider:
    def get(self) -> JIRA:
        return JIRA(os.environ['JIRA_URL'], auth=(os.environ['JIRA_USER'], os.environ['JIRA_PASSWORD']))
