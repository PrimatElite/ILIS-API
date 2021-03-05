from dateutil import parser


def get_version():
    with open('VERSION') as version_file:
        version = version_file.read()
    return version.strip()


def datetime_to_str(dt):
    return dt.replace(microsecond=0).isoformat()


def validate_iso8601(str_val):
    try:
        parser.parse(str_val)
        return True
    except:
        pass
    return False
