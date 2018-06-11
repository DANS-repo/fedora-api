#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import unittest

import logging

import sys

import xml.etree.ElementTree as ET

from fedora.utils import sha1_for_file

from fedora.rest.api import Fedora
from fedora.rest.ds import DatastreamProfile

test_file = "easy-file:219890"
test_dataset = "easy-dataset:5958"

#@unittest.skip("on-line test")
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
        cls.fedora = Fedora.from_file(cfg_file=cfg_file)

    @unittest.skip
    def test_reset(self):
        old = str(self.fedora)
        #Fedora.reset()
        cfg_file = os.path.join(os.path.expanduser("~"), "src", "teasy.cfg")
        self.fedora = Fedora.from_file(cfg_file=cfg_file)
        new = str(self.fedora)
        self.assertNotEqual(old, new)
        self.assertEqual(self.fedora, Fedora())

    # auth required
    def test_object_xml(self):
        objectxml = self.fedora.object_xml(test_file)
        #print(objectxml)
        self.assertTrue(objectxml.startswith("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"))

    def test_datastream_rels_ext(self):
        datastream = self.fedora.datastream(test_file, "RELS-EXT")
        #print(datastream)
        self.assertTrue("<rdf:RDF xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\">" in datastream)

    # auth required
    def test_datastream_easy_file_metadata(self):
        datastream = self.fedora.datastream(test_file, "EASY_FILE_METADATA", content_format="xml")
        #print(datastream)
        self.assertTrue(datastream.startswith("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"))

    # no auth required -> the file it self can be downloaded without auth
    def test_datastream_easy_file_metadata_no_content(self):
        datastream = self.fedora.datastream(test_file, "EASY_FILE_METADATA")
        #print(datastream)
        self.assertTrue("<fimd:file-item-md" in datastream)

    def test_datastream_easy_administrative_metadata_no_content(self):
        datastream = self.fedora.datastream(test_dataset, "AMD")
        print(datastream)
        self.assertTrue("<damd:administrative-md" in datastream)

    # auth required
    def test_datastream_easy_file(self):
        datastream = self.fedora.datastream(test_file, "EASY_FILE", content_format="xml")
        #print(datastream)
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
        #print(result)

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

    @unittest.skip("Ignore post methods")
    def test_ingest(self):
        response = self.fedora.ingest(label='A label', namespace='tester')
        print(response)

    @unittest.skip("Ignore post methods")
    def test_add_managed_datastream(self):
        filepath = 'resources/license.pdf'
        sha1 = sha1_for_file(filepath)
        pid = 'easy-dataset:890'
        ds_id = 'DATASET_LICENSE'
        ds_label = 'license.pdf'
        mediatype = 'application/pdf'
        response = self.fedora.add_managed_datastream(pid, ds_id, ds_label, filepath, mediatype, sha1)
        print(response)

    def test_list_datastreams(self):
        pid = 'easy-dataset:450'
        text = self.fedora.list_datastreams(pid)
        #print(text)

    @unittest.skip('Ignore put methods')
    def test_modify_datastream(self):
        # get the existing datastream 'AMD'
        ET.register_namespace('damd', 'http://easy.dans.knaw.nl/easy/dataset-administrative-metadata/')
        ET.register_namespace('wfs', 'http://easy.dans.knaw.nl/easy/workflow/')
        xml = self.fedora.datastream(test_dataset, "AMD")
        root = ET.fromstring(xml)
        eldp = root.find('depositorId')
        existing_depositor_id = eldp.text
        new_depositor_id = existing_depositor_id[::-1]
        print('changing', existing_depositor_id, 'to', new_depositor_id)

        eldp.text = new_depositor_id
        doc = ET.ElementTree(element=root)

        folder = os.path.join(os.path.expanduser("~"), "tmp", "fedora_modify")
        os.makedirs(folder, exist_ok=True)
        local_path = os.path.join(folder, 'damd.xml')
        doc.write(local_path, encoding='UTF-8', xml_declaration=True)

        response = self.fedora.modify_datastream(test_dataset, 'AMD',
                                                 ds_label='Administrative metadata for this dataset',
                                                 filepath=local_path,
                                                 mediatype='application/xml',
                                                 formatURI='http://easy.dans.knaw.nl/easy/dataset-administrative-metadata/',
                                                 logMessage='testing modify datastream')
        print(response)
        self.assertEqual(200, response.status_code)

        xml = self.fedora.datastream(test_dataset, "AMD")
        root = ET.fromstring(xml)
        eldp = root.find('depositorId')
        self.assertEqual(new_depositor_id, eldp.text)

        dsp = DatastreamProfile(test_dataset, 'AMD', self.fedora)
        dsp.from_xml(response.text)
        print(dsp.props)

