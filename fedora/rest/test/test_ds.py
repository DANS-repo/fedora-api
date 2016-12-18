#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

import logging

import sys

from fedora.rest.api import Fedora
from fedora.rest.ds import DatastreamProfile

connection_parameter_file = "teasy.csv"
test_file = "easy-file:219890"


class TestDatastreamProfile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cfg_file = os.path.join(os.path.expanduser("~"), "src", connection_parameter_file)
        with open(cfg_file) as cfg:
            line = cfg.readline()
        host, port, username, password = line.split(",")
        if not host.startswith("http"):
            host = "http://" + host
        Fedora(host, port, username, password)

        # set up logging
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_fetch(self):
        dsp = DatastreamProfile(test_file, "EASY_FILE")
        dsp.fetch()
        print(dsp.__dict__)