import arrow
from pyckson import parse, serialize
from pymongo.database import Database
from pynject import pynject

from antibot.model.user import User
from antibot.tools import updater


@updater
class ErrorCount:
    def __init__(self, user: User, month: str, count: int):
        self.user = user
        self.month = month
        self.count = count


@pynject
class ErrorsRepository:
    def __init__(self, db: Database):
        self.collection = db['jira_error_count']

    @property
    def month(self) -> str:
        return arrow.utcnow().format('YYYY-MM')

    def get(self, user: User) -> ErrorCount:
        doc = self.collection.find_one({'user.id': user.id, 'month': self.month})
        if doc is None:
            return ErrorCount(user, self.month, 0)
        else:
            return parse(ErrorCount, doc)

    def update(self, error: ErrorCount):
        self.collection.update({'user.id': error.user.id, 'month': error.month}, serialize(error), upsert=True)

    def get_and_inc(self, user: User) -> int:
        error = self.get(user)
        error = error.update(count=error.count + 1)
        self.update(error)
        return error.count
