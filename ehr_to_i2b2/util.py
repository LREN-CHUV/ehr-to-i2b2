import logging
import re
from datetime import datetime
from datetime import timedelta


DEFAULT_DATE = datetime(1, 1, 1)
INIT_MSFT_TIMESTAMP = datetime(year=1899, month=12, day=31)
ITALIAN_MONTHS = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]


def normalize_date(date):
    try:
        return datetime.strptime(date, "%d-%b-%Y")
    except ValueError:
        pass
    try:
        return datetime.strptime(date, "%d/%m/%Y")
    except ValueError:
        pass
    try:
        return parse_custom_date(date, ITALIAN_MONTHS)
    except ValueError:
        pass
    try:
        return INIT_MSFT_TIMESTAMP + timedelta(int(date))
    except ValueError:
        pass

    logging.warning("Cannot normalize date %s !", str(date))
    return None


def parse_custom_date(date, months):
    matches = re.fullmatch("([0-3]?[0-9])-([a-zA-Z]{3})-([0-9][0-9])", date)
    try:
        day = int(matches.group(1))
        month = months.index(matches.group(2).lower()) + 1
        year = int(matches.group(3)) + 1900
        return datetime(year, month, day)
    except (AttributeError, IndexError, ValueError):
        raise ValueError


def normalize_sex(sex):
    if sex.upper()[0] in ['H', 'M']:
        return 'M'
    elif sex.upper()[0] in ['F']:
        return 'F'
    return None


def compute_age(years=0, months=0):
    if months <= 0:
        return years
    return years + months / 12.0


def find_type(val):
    try:
        float(val)
        return 'N'
    except ValueError:
        return 'T'
