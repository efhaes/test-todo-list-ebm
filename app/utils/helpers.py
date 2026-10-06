
from datetime import datetime, timezone

import uuid_utils 


def generate_uuid7() -> str:
    return str(uuid_utils.uuid7())


def utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)