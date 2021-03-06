from datetime import datetime
from dateutil import parser


def get_version() -> str:
    with open('VERSION') as version_file:
        version = version_file.read()
    return version.strip()


def datetime2str(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def validate_iso8601(value: str):
    try:
        parser.parse(value)
        return True
    except:
        pass
    return False
