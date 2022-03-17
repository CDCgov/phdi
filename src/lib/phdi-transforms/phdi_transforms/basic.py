def transform_name(raw: str) -> str:
    """trim spaces and force uppercase

    >>> transform_name(" JohN Doe ")
    'JOHN DOE'
    """

    raw = [x for x in raw if not x.isnumeric()]
    raw = "".join(raw)
    raw = raw.upper()
    raw = raw.strip()
    return raw


def transform_phone(raw: str) -> str:
    """Make sure it's 10 digits, remove everything else

    >>> transform_phone("(555) 555-1212")
    '5555551212'
    """

    raw = [x for x in raw if x.isnumeric()]
    raw = "".join(raw)
    if len(raw) != 10:
        raw = None
    return raw
