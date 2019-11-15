from typing import Optional

from autovalue import autovalue


@autovalue
class User:
    def __init__(self, id: str, display_name: str, email: Optional[str] = None):
        self.id = id
        self.display_name = display_name
        self.email = email
