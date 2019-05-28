from typing import Optional

from pyckson import no_camel_case


@no_camel_case
class Profile:
    def __init__(self, display_name: str, email: Optional[str] = None):
        self.display_name = display_name
        self.email = email


@no_camel_case
class Member:
    def __init__(self, id: str, profile: Profile):
        self.id = id
        self.profile = profile
