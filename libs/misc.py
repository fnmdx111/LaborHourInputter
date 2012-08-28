# encoding: utf-8
import calendar
from itertools import izip
import datetime


def take(iterable, by=5):
    """e.g. list(take([1, 2, 3, 4, 5], by=2))
         => [[1, 2], [3, 4], [5]]
    note: the iterable must support slicing"""
    while iterable:
        if len(iterable) < by:
            yield iterable
        else:
            yield iterable[:by]
        iterable = iterable[by:]


def take_adj(iterable, by=2):
    """e.g. list(take_adj([1, 2, 3, 4, 5], by=3))
         => [[1, 2, 3], [2, 3, 4], [3, 4, 5], [4, 5]]
    note: though `take_adj' will handle the condition when `len(iterable) % by != 0', but
          it is strongly recommended that you choose your `by' carefully"""
    while iterable:
        if len(iterable) < by:
            yield iterable + [None]
            break
        else:
            yield iterable[:by]
        iterable = iterable[1:]


def interleave(*iterables):
    """e.g. list(interleave([1, 2, 3], ['a', 'b', 'c'], ['A', 'B', 'C']))
         => [1, 'a', 'A', 2, 'b', 'B', 3, 'c', 'C']"""
    for zipped in izip(*iterables):
        for item in zipped:
            yield item


def concat_prf(prf):
    """return a function that concatenate the given prefix and it's parameter"""
    return lambda x: prf + str(x)


def get_today():
    return datetime.date.today()


def _get_dates(dt):
    if dt.day >= 28:
        # it's a new month
        if dt.month + 1 > 12:
            date1 = datetime.date(dt.year + 1, 1, 27)
        else:
            date1 = datetime.date(dt.year, dt.month + 1, 27)
        date2 = datetime.date(dt.year, dt.month, 28)
    else:
        if dt.month - 1 < 1:
            date2 = datetime.date(dt.year - 1, 12, 28)
        else:
            date2 = datetime.date(dt.year, dt.month - 1, 28)
        date1 = datetime.date(dt.year, dt.month, 27)

    return date1, date2


def get_month_days(dt=get_today()):
    d1, d2 = _get_dates(dt)

    return range(d2.day, calendar.monthrange(d2.year, d2.month)[1] + 1) +\
           range(1, d1.day + 1)


def get_month_day_num(dt=get_today()):
    dt = get_today() if not dt else dt
    d1, d2 = _get_dates(dt)
    delta = d1 - d2

    return delta.days + 1


def sort_dict_keys_numerically(d):
    """return key-value pairs that are sorted by the `key'"""
    return sorted(d.iteritems(),
                  cmp=lambda x, y: cmp(int(x[0]), int(y[0])))


def invert_dict(d):
    """invert the given dict as d<k, v> => d'<v, k>"""
    return dict(map(lambda (key, value): (value, key), d.iteritems()))



if __name__ == '__main__':
    print get_month_day_num()
    print get_month_days()
    print invert_dict({1: 'a', 2: 'b', 3: 'c'})



