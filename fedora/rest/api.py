#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import urllib.parse

import requests

LOG = logging.getLogger(__name__)
FEDORA = None


class FedoraException(RuntimeError):
    pass


class Fedora(object):

    def __init__(self, host, port, username, password):
        self.url = host + ":" + str(port) + "/fedora"
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0'}
        self.session.auth = (username, password)
        global FEDORA
        FEDORA = self

    def as_text(self, url):
        response = self.session.get(url)
        if response.status_code == requests.codes.ok:
            return response.text
        else:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))

    def object_xml(self, object_id):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-getObjectXML
        """
        url = self.url + "/objects/" + object_id + "/objectXML"
        return self.as_text(url)

    def datastream(self, object_id, ds_id, content_format="content"):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-getDatastream
        """
        if content_format == "content":
            postfix = "/content"
        else:
            postfix = "?format=" + content_format
        url = self.url + "/objects/" + object_id + "/datastreams/" + ds_id + postfix
        return self.as_text(url)

    def add_relationship(self, subj_id, predicate, obj, is_literal=False, data_type=None):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-addRelationship
        """
        url = self.url + "/objects/" + subj_id + "/relationships/new?" \
              + self.create_rdf_statement(subj_id, predicate, obj, is_literal, data_type)
        response = self.session.post(url)
        if response.status_code != requests.codes.ok:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))

    def purge_relationship(self, subj_id, predicate, obj, is_literal=False, data_type=None):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-purgeRelationship
        """
        url = self.url + "/objects/" + subj_id + "/relationships?" \
              + self.create_rdf_statement(subj_id, predicate, obj, is_literal, data_type)
        response = self.session.delete(url)
        if response.status_code == requests.codes.ok:
            return response.text == "true"
        else:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))

    @staticmethod
    def create_rdf_statement(subj_id, predicate, obj, is_literal=False, data_type=None):
        """
        Creates a url-encoded rdf querystring in the format "subject= &predicate= &object= [&isLiteral= [&datatype= ]]"
        """
        subject = "info:fedora/" + subj_id
        query = {"subject": subject, "predicate": predicate, "object": obj}
        if is_literal:
            query.update({"isLiteral": "true"})
            if data_type:
                query.update({"datatype": data_type})
        return urllib.parse.urlencode(query)







