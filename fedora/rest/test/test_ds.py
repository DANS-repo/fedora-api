#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import sys
import unittest

from fedora.rest.api import Fedora
from fedora.rest.ds import DatastreamProfile, FileItemMetadata, RelsExt

connection_parameter_file = "teasy.csv"
test_file = "easy-file:1950715"


@unittest.skip("on-line test")
class TestDatastreamProfile(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set up logging
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

        # set up connection to teasy
        Fedora(cfg_file=os.path.expanduser("~/src/teasy.cfg"))

    def test_fetch_easy_file_profile(self):
        dsp = DatastreamProfile(test_file, "EASY_FILE")
        dsp.fetch()
        print(dsp.props)
        self.assertEqual(15, len(dsp.props))
        self.assertIsNotNone(dsp.ds_size)

    def test_fetch_easy_file_metadata_profile(self):
        dsp = DatastreamProfile(test_file, "EASY_FILE_METADATA")
        dsp.fetch()
        print(dsp.props)
        self.assertEqual(15, len(dsp.props))
        self.assertIsNotNone(dsp.ds_size)

    def test_fetch_rels_ext_profile(self):
        dsp = DatastreamProfile(test_file, "RELS-EXT")
        dsp.fetch()
        print(dsp.props)
        self.assertEqual(15, len(dsp.props))
        self.assertIsNotNone(dsp.ds_size)


class TestFileItemMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set up logging
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_fetch(self):
        fim = FileItemMetadata(test_file)
        fim.fetch()
        print(fim.props)
        self.assertEqual(10, len(fim.props))
        self.assertIsNotNone(fim.fmd_size)


class TestRelsExt(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # set up logging
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
        ch.setFormatter(formatter)
        root.addHandler(ch)

    def test_fetch(self):
        rex = RelsExt(test_file)
        rex.fetch()
        dsid = rex.get_is_subordinate_to()
        print(dsid)
