from typing import List

from antibot.flow.matchers import Matcher
from pynject.decorators import singleton


class QuickCommand:
    def __init__(self, matcher: Matcher, runner, auto_delete: bool):
        self.auto_delete = auto_delete
        self.runner = runner
        self.matcher = matcher


@singleton
class QuickiesRepository:
    def __init__(self):
        self._quickies = []

    @property
    def quickies(self) -> List[QuickCommand]:
        return self._quickies

    def add_quicky(self, quick: QuickCommand):
        self._quickies.append(quick)

    def remove_quicky(self, quick: QuickCommand):
        self._quickies.remove(quick)
