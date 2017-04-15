from urllib.parse import urlparse, urljoin

import datetime
from flask import request, url_for


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
           ref_url.netloc == test_url.netloc


class FutureDateException(Exception):
    pass


class DateParseException(Exception):
    pass


def parse_date(date: str):
    """Given a date string parse it and return back a date object and resolution.

    date is always a string.
    Could be 'today' or 'yesterday' or 'YYYY/MM/DD' or 'YYYY/MM' or 'YYYY'
    if it is today or yesterday or YYYY/MM/DD format, resolution is 'day'
        meaning we need to get entries for that particular date.
    if it is 'YYYY/MM' resolution is 'month'
        meaning we need to get entries for the entire month.
    if it is 'YYYY' resolution is 'year'
        meaning we need to get entries for the entire year.

    If the date is in future, it throws a FutureDateException, as we don't want to edit for future entries.
    and if the date is not parseable, it throws a DateParseException.
    """
    today = datetime.date.today()
    try:
        if date.lower() == 'today':
            date_obj = today
            resolution = 'day'
        elif date.lower() == 'yesterday':
            date_obj = today - datetime.timedelta(days=1)
            resolution = 'day'
        else:
            slash_count = date.count('/')
            if slash_count == 2:
                # year/month/date format
                date_obj = datetime.datetime.strptime(date, '%Y/%m/%d').date()
                resolution = 'day'
            elif slash_count == 1:
                # year/month format
                date_obj = datetime.datetime.strptime(date, '%Y/%m').date()
                resolution = 'month'
            elif slash_count == 0:
                # year format
                date_obj = datetime.datetime.strptime(date, '%Y').date()
                resolution = 'year'
            else:
                # fallback to today
                date_obj = today
                resolution = 'day'

            if date_obj - today > 0:
                raise FutureDateException("Trying to edit the future.")

    except ValueError:
        raise DateParseException("Couldn't parse date")
    return date_obj, resolution
