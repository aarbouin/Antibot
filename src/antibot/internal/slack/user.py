from dataclasses import dataclass
from typing import Optional

from pyckson import no_camel_case


@no_camel_case
@dataclass
class Profile:
    display_name: str
    real_name: str
    email: Optional[str]


@no_camel_case
@dataclass
class Member:
    id: str
    profile: Profile
