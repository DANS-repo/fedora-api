#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

import logging

import sys

from fedora.rest.api import Fedora
from fedora.worker import Worker, LocalWorker


@unittest.skip("on-line test")
class TestWorker(unittest.TestCase):
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

    def test_id_iter(self):
        worker = Worker()

        ids = ["1", "2", "3"]
        rids = []
        for id in worker.id_iter(ids):
            rids.append(id)
        self.assertEqual(rids, ids)

        ids = ["one", "two", "three"]
        rids = []
        dir_path = os.path.dirname(os.path.realpath(__file__))
        id_list = os.path.join(dir_path, "resources/id-list.txt")
        for id in worker.id_iter(id_list):
            rids.append(id)
        self.assertEqual(rids, ids)

    def test_download_batch(self):
        id_list = ["easy-file:208104", "easy-file:238535", "easy-file:75089"]
        dump_dir = os.path.join(os.path.expanduser("~"), "tmp", "worker-downloads")
        log_file = os.path.join(dump_dir, "worker-log.csv")

        worker = Worker()
        checksum_error_count = worker.download_batch(id_list, dump_dir, log_file)
        self.assertEqual(0, checksum_error_count)


@unittest.skip
class TestLocalWorker(unittest.TestCase):
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

    def test_verify_checksums(self):
        dump_dir = os.path.join(os.path.expanduser("~"), "tmp", "worker-downloads")
        log_file = os.path.join(dump_dir, "worker-log.csv")

        worker = LocalWorker()
        checksum_error_count = worker.verify_checksums_local(log_file)
        self.assertEqual(0, checksum_error_count)


