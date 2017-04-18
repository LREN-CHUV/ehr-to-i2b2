def normalize_sex(sex):
    if sex.upper()[0] in ['H', 'M']:
        return 'M'
    elif sex.upper()[0] in ['F']:
        return 'F'


def compute_age(years=0, months=0):
    if months <= 0:
        return years
    return years + 12.0/months


def find_type(val):
    try:
        float(val)
        return 'N'
    except ValueError:
        return 'T'
