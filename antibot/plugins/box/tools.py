from datetime import datetime

import arrow


def today() -> datetime:
    return arrow.utcnow().replace(hour=0, minute=0, second=0, microsecond=0).datetime
