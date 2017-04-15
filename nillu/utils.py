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


def parse_date(date):
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
