from contextlib import contextmanager

from pyckson import parse
from pymongo.database import Database
from pynject import pynject


@pynject
class Storage:
    def __init__(self, name: str, mongo: Database):
        self.collection = mongo[name]

    def get(self, key, default=None, cls=None):
        result = self.collection.find_one({'_id': key})
        result = result['value'] if result is not None else default
        result = parse(cls, result) if cls is not None else result
        return result

    def save(self, key, value):
        self.collection.update({'_id': key}, {'_id': key, 'value': value}, upsert=True)

    @contextmanager
    def __getitem__(self, item):
        data = self.get(item)
        yield data
        self.save(item, data)


@pynject
class StorageFactory:
    def __init__(self, db: Database):
        self.db = db

    def get(self, cls) -> Storage:
        return Storage(cls.__name__, self.db)
