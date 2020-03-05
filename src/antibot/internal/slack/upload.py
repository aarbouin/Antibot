import re

from pyckson import no_camel_case


@no_camel_case
class File:
    def __init__(self, id: str, permalink: str, permalink_public: str, name: str):
        self.id = id
        self.permalink = permalink
        self.permalink_public = permalink_public
        self.name = name

        match = re.match(r'https://slack-files.com/(.*)-(.*)-(.*)', self.permalink_public)
        self.team_id = match.group(1)
        self.secret = match.group(3)

    @property
    def public_link(self):
        return 'https://files.slack.com/files-pri/{}-{}/{}?pub_secret={}'.format(
            self.team_id,
            self.id,
            self.permalink.split('/')[-1],
            self.secret
        )
