# encoding: utf-8
from itertools import izip


def take(iterable, by=5):
    while iterable:
        if len(iterable) < by:
            yield iterable
        else:
            yield iterable[:by]
        iterable = iterable[by:]


def take_adj(iterable, by=2):
    while iterable:
        if len(iterable) < by:
            yield iterable + [None]
            break
        else:
            yield iterable[:by]
        iterable = iterable[1:]


def interleave(*iterables):
    for zipped in izip(*iterables):
        for item in zipped:
            yield item


def concat_prf(prf):
    return lambda x: prf + str(x)

if __name__ == '__main__':
    for item, prime in take_adj(range(5)):
        print item, prime

    for item in interleave(range(5), range(5, 10), range(10, 15)):
        print item



