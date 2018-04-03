#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

import logging

import sys

from fedora.rest.api import Fedora

test_file = "easy-file:219890"

@unittest.skip("on-line test")
class TestFedora(unittest.TestCase):

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

        cfg_file = os.path.join(os.path.expanduser("~"), "src", "teasy.cfg")
        cls.fedora = Fedora(cfg_file=cfg_file)

    @unittest.skip
    def test_reset(self):
        old = str(self.fedora)
        Fedora.reset()
        cfg_file = os.path.join(os.path.expanduser("~"), "src", "teasy.cfg")
        self.fedora = Fedora(cfg_file=cfg_file)
        new = str(self.fedora)
        self.assertNotEqual(old, new)
        self.assertEqual(self.fedora, Fedora())

    # auth required
    def test_object_xml(self):
        objectxml = self.fedora.object_xml(test_file)
        print(objectxml)
        self.assertTrue(objectxml.startswith("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"))

    def test_datastream_rels_ext(self):
        datastream = self.fedora.datastream(test_file, "RELS-EXT")
        #print(datastream)
        self.assertTrue("<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">" in datastream)

    # auth required
    def test_datastream_easy_file_metadata(self):
        datastream = self.fedora.datastream(test_file, "EASY_FILE_METADATA", content_format="xml")
        print(datastream)
        self.assertTrue(datastream.startswith("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"))

    # no auth required -> the file it self can be downloaded without auth
    def test_datastream_easy_file_metadata_no_content(self):
        datastream = self.fedora.datastream(test_file, "EASY_FILE_METADATA")
        print(datastream)
        self.assertTrue("<fimd:file-item-md" in datastream)

    # auth required
    def test_datastream_easy_file(self):
        datastream = self.fedora.datastream(test_file, "EASY_FILE", content_format="xml")
        print(datastream)
        self.assertTrue(datastream.startswith("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"))

    def test_datastream_easy_file_no_content(self):
        datastream = self.fedora.datastream(test_file, "EASY_FILE")
        #print(datastream)
        # downloads the file

    # auth required
    def test_add_relationship(self):
        # the datatype dateTime should not be set, because of exception in
        # nl.knaw.dans.common.fedora.rdf.FedoraRelationsConverter.rdfToRelations
        self.fedora.add_relationship(test_file,
                                     "https://www.w3.org/TR/2012/CR-prov-o-20121211/#wasDerivedFrom",
                                     "info:fedora/easy-file:1")
        self.fedora.add_relationship(test_file,
                                     "https://www.w3.org/TR/2012/CR-prov-o-20121211/#wasGeneratedBy",
                                     "http://dans.knaw.nl/aips/55e73f76-5b10-11e6-9822-685b357e70b6.5")
        self.fedora.add_relationship(test_file,
                                     "https://www.w3.org/TR/2012/CR-prov-o-20121211/#generatedAtTime",
                                     "2016-11-23T00:00:00Z", is_literal=True) #,
                                     #data_type="http://www.w3.org/2001/XMLSchema#dateTime")

    # auth required
    def test_purge_relationship(self):
        self.fedora.purge_relationship(test_file,
                                       "https://www.w3.org/TR/2012/CR-prov-o-20121211/#wasDerivedFrom",
                                       "info:fedora/easy-file:1")
        self.fedora.purge_relationship(test_file,
                                       "https://www.w3.org/TR/2012/CR-prov-o-20121211/#wasGeneratedBy",
                                       "http://dans.knaw.nl/aips/55e73f76-5b10-11e6-9822-685b357e70b6.5")
        self.fedora.purge_relationship(test_file,
                                       "https://www.w3.org/TR/2012/CR-prov-o-20121211/#generatedAtTime",
                                       "2016-11-23T00:00:00Z", is_literal=True) #,
                                       #data_type="http://www.w3.org/2001/XMLSchema#dateTime")

    def test_add_mail_address_to_rdf(self):
        self.fedora.add_relationship(test_file,
                                     "http://www.w3.org/ns/prov#wasAssociatedWith",
                                     "mailto:firstname.lastname@dans.knaw.nl")

    def test_purge_mail_address_to_rdf(self):
        self.fedora.purge_relationship(test_file,
                                     "http://www.w3.org/ns/prov#wasAssociatedWith",
                                     "mailto:firstname.lastname@dans.knaw.nl")

    # # Adding blind nodes to RELS-EXT is not possible.
    # def test_add_blind_node(self):
    #     self.fedora.add_relationship(test_file,
    #                                  "http://testing.com/hasMultiFacetProp",
    #                                  "_:bnode42multifacetprop")
    #     self.fedora.add_relationship2(test_file,
    #                                   "_:bnode42multifacetprop",
    #                                   "http://dans.knaw.nl/ontologies/conversions#isConversionOf",
    #                                   "info:fedora/easy-file:2")
    #     self.fedora.add_relationship2(test_file,
    #                                   "_:bnode42multifacetprop",
    #                                   "http://dans.knaw.nl/ontologies/conversions#conversionDate",
    #                                    "2016-11-23T00:00:00.000Z", is_literal=True,
    #                                    data_type="http://www.w3.org/2001/XMLSchema#dateTime")

    def test_download(self):
        folder = os.path.join(os.path.expanduser("~"), "tmp", "fedora_download")
        meta = self.fedora.download(test_file, "EASY_FILE", folder=folder)
        #print(meta)
        self.fedora.download(test_file, "RELS-EXT", folder=folder)
        self.fedora.download(test_file, "DC", folder=folder)
        self.fedora.download(test_file, "EASY_FILE_METADATA", folder=folder)

    def test_find_objects(self):
        query = "cDate>=2015-01-01 pid~easy-dataset:* state=A"
        result = self.fedora.find_objects(query)
        print(result)

    # auth required because of post. can query unauthorized with get.
    def test_risearch(self):
        datasetId = "easy-dataset:450"
        query = \
                  "PREFIX dans: <http://dans.knaw.nl/ontologies/relations#> " \
                + "PREFIX fmodel: <info:fedora/fedora-system:def/model#> " \
                \
                + "SELECT ?s " \
                + "WHERE " \
                + "{ " \
                + "   ?s dans:isSubordinateTo <info:fedora/" + datasetId + "> . " \
                + "   ?s fmodel:hasModel <info:fedora/easy-model:EDM1FILE> " \
                + "}"
        print(query)
        result = self.fedora.risearch(query)
        print(result)

    @unittest.skip("Ignore Post methods")
    def test_get_next_pid(self):
        response = self.fedora.get_next_pid(namespace='easy-file')
        print(response)
        # easy-file:350704

    def test_ingest(self):
        response = self.fedora.ingest(label='A label', namespace='tester')
        print(response)
