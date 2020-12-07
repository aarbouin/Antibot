from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class User:
    id: str
    display_name: str
    email: Optional[str]
    all_names: List[str] = field(default_factory=list)
