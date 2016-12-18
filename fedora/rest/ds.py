#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import xml.etree.ElementTree as ET

from fedora.rest import api

ns = {"dsp" : "http://www.fedora.info/definitions/1/0/management/"}


class DatastreamProfile(object):

    def __init__(self, object_id, ds_id):
        self.fedora = api.get_fedora()
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

    def fetch(self):
        xml = self.fedora.datastream(self.object_id, self.ds_id, content_format="xml")
        root = ET.fromstring(xml)
        self.ds_label = self.__text__(root.find("dsp:dsLabel", ns))
        self.ds_version_id = self.__text__(root.find("dsp:dsVersionID", ns))
        self.ds_creation_date = self.__text__(root.find("dsp:dsCreateDate", ns))
        self.ds_state = self.__text__(root.find("dsp:dsState", ns))
        self.ds_mime = self.__text__(root.find("dsp:dsMIME", ns))
        self.ds_format_uri = self.__text__(root.find("dsp:dsFormatURI", ns))
        self.ds_control_group = self.__text__(root.find("dsp:dsControlGroup", ns))
        self.ds_size = self.__int__(root.find("dsp:dsSize", ns))
        self.ds_versionable = self.__bool__(root.find("dsp:dsVersionable", ns))
        self.ds_info_type = self.__text__(root.find("dsp:dsInfoType", ns))
        self.ds_location = self.__text__(root.find("dsp:dsLocation", ns))
        self.ds_location_type = self.__text__(root.find("dsp:dsLocationType", ns))
        self.ds_checksum_type = self.__text__(root.find("dsp:dsChecksumType", ns))
        self.ds_checksum = self.__text__(root.find("dsp:dsChecksum", ns))

    @staticmethod
    def __text__(element):
        if element is None:
            return None
        else:
            return element.text

    @staticmethod
    def __int__(element):
        if element is None:
            return None
        else:
            return int(element.text)

    @staticmethod
    def __bool__(element):
        if element is None:
            return None
        else:
            return element.text == "true"


