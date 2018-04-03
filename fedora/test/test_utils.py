#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import unittest

from fedora import utils


class TestUtils(unittest.TestCase):

    def test_parse_to_date(self):
        w3 = utils.as_w3c_datetime("2016-12-12")
        self.assertEqual("2016-12-11T23:00Z", w3)
        w3 = utils.as_w3c_datetime("Wed, 21 Dec 2016 12:31:38 GMT")
        self.assertEqual("2016-12-21T12:31:38Z", w3)
        # ValueError
        err = utils.as_w3c_datetime("123456789")
        self.assertEqual("Error: 123456789", err)

    @unittest.skip("not a test")
    def test_csv_dialects(self):
        print(csv.list_dialects())
        # ['excel-tab', 'excel', 'unix']
        # if you want the standard RFC4180 then roll your own.
