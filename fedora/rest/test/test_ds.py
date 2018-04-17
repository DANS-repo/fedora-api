#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import sys
import unittest

from fedora.rest.api import Fedora
from fedora.rest.ds import DatastreamProfile, FileItemMetadata, RelsExt, AdministrativeMetadata, ObjectDatastreams, \
    EasyMetadata

test_file = "easy-file:1950715"
test_dataset = "easy-dataset:5958"


#@unittest.skip("on-line test")
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
        cfg_file = os.path.join(os.path.expanduser("~"), "src", "teasy.cfg")
        cls.fedora = Fedora(cfg_file=cfg_file)

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


class TestAdministrativeMetadata(unittest.TestCase):

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

    def test_fetch(self):
        amd = AdministrativeMetadata(test_dataset)
        amd.fetch()
        print(amd.props)


class TestEasyMetadata(unittest.TestCase):

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

    def test_fetch(self):
        emd = EasyMetadata('easy-dataset:20')
        emd.fetch()
        self.assertEqual('10.5072/dans-249-exct', emd.doi)


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


class TestObjectDatastreams(unittest.TestCase):

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
        Fedora.reset()
        cfg_file = os.path.join(os.path.expanduser("~"), "src", "teasy.cfg")
        cls.fedora = Fedora(cfg_file=cfg_file)

    def test_fetch(self):
        pid = 'easy-dataset:450'
        ods = ObjectDatastreams(pid)
        dss = ods.fetch()
        print(dss['DATASET_LICENSE'])
        print('EMD' in dss)

