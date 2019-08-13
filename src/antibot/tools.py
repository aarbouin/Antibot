import traceback
from contextlib import contextmanager
from datetime import datetime
from inspect import signature
from json import dumps
from typing import Optional

import arrow

from antibot.slack.api import SlackApi


def updater(cls):
    attributes = [name for name in signature(cls.__init__).parameters.keys() if name != 'self']

    def update(self, **kwargs) -> cls:
        cls_args = {attr: getattr(self, attr) for attr in attributes}
        for k, v in kwargs.items():
            cls_args[k] = v
        return cls(**cls_args)

    setattr(cls, 'update', update)

    return cls


def today() -> datetime:
    return arrow.utcnow().floor('day').datetime


def yesterday() -> datetime:
    return arrow.utcnow().floor('day').shift(days=-1).datetime


@contextmanager
def notify_errors(api: SlackApi, query: Optional[dict] = None):
    try:
        yield
    except Exception:
        date = datetime.now().isoformat()
        api.upload_file('bot',
                        filename='error-{}-stacktrace.txt'.format(date),
                        title='Antibot error stacktrace from {}'.format(date),
                        content=traceback.format_exc().encode('utf-8'))
        if query:
            api.upload_file('bot',
                            filename='error-{}-query.json'.format(date),
                            title='Antibot error query from {}'.format(date),
                            content=dumps(query, indent=2).encode('utf-8'))
        raise
