#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET
import pandas as pd
import rdflib

from fedora.rest.api import Fedora, FedoraException

ns = {"dsp": "http://www.fedora.info/definitions/1/0/management/",
      "damd": "http://easy.dans.knaw.nl/easy/dataset-administrative-metadata/",
      "dc": "http://purl.org/dc/elements/1.1/",
      "emd": "http://easy.dans.knaw.nl/easy/easymetadata/",
      "eas": "http://easy.dans.knaw.nl/easy/easymetadata/eas/"}


def __text__(element):
    if element is None:
        return None
    else:
        return element.text


def __int__(element):
    if element is None:
        return None
    else:
        return int(element.text)


def __bool__(element):
    if element is None:
        return None
    else:
        return element.text == "true"


class DatastreamProfile(object):

    def __init__(self, object_id, ds_id, fedora):
        self.fedora = fedora
        self.object_id = object_id
        self.ds_id = ds_id

        self.ds_label = None
        self.ds_version_id = None
        self.ds_creation_date = None
        self.ds_state = None
        self.ds_mime = None
        self.ds_format_uri = None
        self.ds_control_group = None
        self.ds_size = None
        self.ds_versionable = None
        self.ds_info_type = None
        self.ds_location = None
        self.ds_location_type = None
        self.ds_checksum_type = None
        self.ds_checksum = None
        self.props = {}

    def fetch(self):
        xml = self.fedora.datastream(self.object_id, self.ds_id, content_format="xml")
        self.from_xml(xml)

    def from_xml(self, xml):
        root = ET.fromstring(xml)
        self.ds_label = __text__(root.find("dsp:dsLabel", ns))
        self.ds_version_id = __text__(root.find("dsp:dsVersionID", ns))
        self.ds_creation_date = __text__(root.find("dsp:dsCreateDate", ns))
        self.ds_state = __text__(root.find("dsp:dsState", ns))
        self.ds_mime = __text__(root.find("dsp:dsMIME", ns))
        self.ds_format_uri = __text__(root.find("dsp:dsFormatURI", ns))
        self.ds_control_group = __text__(root.find("dsp:dsControlGroup", ns))
        self.ds_size = __int__(root.find("dsp:dsSize", ns))
        self.ds_versionable = __bool__(root.find("dsp:dsVersionable", ns))
        self.ds_info_type = __text__(root.find("dsp:dsInfoType", ns))
        self.ds_location = __text__(root.find("dsp:dsLocation", ns))
        self.ds_location_type = __text__(root.find("dsp:dsLocationType", ns))
        self.ds_checksum_type = __text__(root.find("dsp:dsChecksumType", ns))
        self.ds_checksum = __text__(root.find("dsp:dsChecksum", ns))
        self.props = {k: v for k, v in self.__dict__.items() if k.startswith("ds_")}


class FileItemMetadata(object):

    def __init__(self, object_id, fedora):
        self.fedora = fedora
        self.object_id = object_id

        self.fmd_sid = None
        self.fmd_name = None
        self.fmd_parent_sid = None
        self.fmd_dataset_sid = None
        self.fmd_path = None
        self.fmd_mime_type = None
        self.fmd_size = None
        self.fmd_creator_role = None
        self.fmd_visible_to = None
        self.fmd_accessible_to = None
        self.props = {}

    def fetch(self):
        xml = self.fedora.datastream(self.object_id, "EASY_FILE_METADATA")
        root = ET.fromstring(xml)
        # elements in this datastream are not in any particular namespace
        self.fmd_sid = __text__(root.find("sid"))
        self.fmd_name = __text__(root.find("name"))
        self.fmd_parent_sid = __text__(root.find("parentSid"))
        self.fmd_dataset_sid = __text__(root.find("datasetSid"))
        self.fmd_path = __text__(root.find("path"))
        self.fmd_mime_type = __text__(root.find("mimeType"))
        self.fmd_size = __int__(root.find("size"))
        self.fmd_creator_role = __text__(root.find("creatorRole"))
        self.fmd_visible_to = __text__(root.find("visibleTo"))
        self.fmd_accessible_to = __text__(root.find("accessibleTo"))
        self.props = {k: v for k, v in self.__dict__.items() if k.startswith("fmd_")}


class AdministrativeMetadata(object):

    def __init__(self, object_id, fedora):
        if not str(object_id).startswith("easy-dataset"):
            raise FedoraException("object %s has no AMD" % object_id)
        self.fedora = fedora
        self.object_id = object_id

        self.amd_dataset_state = None
        self.amd_previous_state = None
        self.amd_last_state_change = None
        self.amd_depositor_id = None
        self.props = {}

    def fetch(self):
        xml = self.fedora.datastream(self.object_id, "AMD")
        root = ET.fromstring(xml)
        self.amd_dataset_state = __text__(root.find("datasetState"))
        self.amd_previous_state = __text__(root.find("previousState"))
        self.amd_last_state_change = __text__(root.find("lastStateChange"))
        self.amd_depositor_id = __text__(root.find("depositorId"))
        self.props = {k: v for k, v in self.__dict__.items() if k.startswith("amd_")}


class EasyMetadata(object):

    def __init__(self, object_id, fedora):
        if not str(object_id).startswith("easy-dataset"):
            raise FedoraException("object %s has no EMD" % object_id)
        self.fedora = fedora
        self.object_id = object_id

        self.doi = None
        self.urn = None

    def fetch(self):
        xml = self.fedora.datastream(self.object_id, "EMD")
        root = ET.fromstring(xml)
        emd_identifier = root.find("emd:identifier", ns)
        if emd_identifier:
            for child in emd_identifier:
                if '{http://easy.dans.knaw.nl/easy/easymetadata/eas/}scheme' in child.attrib \
                        and child.attrib['{http://easy.dans.knaw.nl/easy/easymetadata/eas/}scheme'] == 'DOI':
                    self.doi = child.text
                if '{http://easy.dans.knaw.nl/easy/easymetadata/eas/}scheme' in child.attrib \
                        and child.attrib['{http://easy.dans.knaw.nl/easy/easymetadata/eas/}scheme'] == 'PID':
                    self.urn = child.text


def dataset_identifiers(dataset_ids, fedora):
    df = pd.DataFrame(columns=['dataset_id', 'doi', 'urn'])
    for easy_id in dataset_ids:
        emd = EasyMetadata(easy_id, fedora)
        emd.fetch()
        fields = {'dataset_id': easy_id, 'doi': emd.doi, 'urn': emd.urn}
        df = df.append(fields, ignore_index=True)
    return df


class RelsExt(object):

    def __init__(self, object_id, fedora):
        self.fedora = fedora
        self.object_id = object_id
        self.graph = rdflib.Graph()
        self.subject = rdflib.URIRef('info:fedora/' + self.object_id)

    def fetch(self):
        self.graph.parse(data=self.fedora.datastream(self.object_id, "RELS-EXT"))

    def get_graph(self):
        return self.graph

    def get_is_subordinate_to(self):
        return \
        str(self.graph.value(self.subject, rdflib.URIRef('http://dans.knaw.nl/ontologies/relations#isSubordinateTo'))).split(
            '/')[1]


class ObjectDatastreams(object):

    def __init__(self, object_id, fedora):
        self.fedora = fedora
        self.object_id = object_id

    def fetch(self):
        xml = self.fedora.list_datastreams(self.object_id)
        root = ET.fromstring(xml)
        dss = {}
        for element in root:
            dss.update({element.attrib['dsid']: element.attrib})
        return dss



