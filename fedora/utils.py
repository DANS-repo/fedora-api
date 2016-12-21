#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import time
from datetime import datetime
from functools import partial

from dateutil import parser


def w3c_datetime(i):
    """ given seconds since the epoch, return a dateTime string.
    from: https://gist.github.com/mnot/246088
    """
    assert type(i) in [int, float]
    year, month, day, hour, minute, second, wday, jday, dst = time.gmtime(i)
    o = str(year)
    if (month, day, hour, minute, second) == (1, 1, 0, 0, 0): return o
    o += '-%2.2d' % month
    if (day, hour, minute, second) == (1, 0, 0, 0): return o
    o += '-%2.2d' % day
    if (hour, minute, second) == (0, 0, 0): return o
    o += 'T%2.2d:%2.2d' % (hour, minute)
    if second != 0:
        o += ':%2.2d' % second
    o += 'Z'
    return o


def w3c_now():
    return w3c_datetime(datetime.now().timestamp())


def as_datetime(text):
    return parser.parse(text)


def as_w3c_datetime(text):
    try:
        return w3c_datetime(parser.parse(text).timestamp())
    except ValueError:
        return "Error: " + text


def sha1_for_file(filename, block_size=2**14):
    """Compute SHA1 digest for a file

    Optional block_size parameter controls memory used to do MD5 calculation.
    This should be a multiple of 128 bytes.
    """
    with open(filename, mode='rb') as f:
        d = hashlib.sha1()
        for buf in iter(partial(f.read, block_size), b''):
            d.update(buf)
    return d.hexdigest()


