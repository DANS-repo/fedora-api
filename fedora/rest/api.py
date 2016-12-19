#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import urllib.parse

import requests

LOG = logging.getLogger(__name__)
CFG_FILE = "src/fedora.cfg"


class FedoraException(RuntimeError):
    pass


class Fedora(object):
    """
    Fedora is a singleton class that expects a configuration file at::

        {user_home}/src/fedora.cfg

    The first line of the file should contain::

        host,port,username,password

    The first time the Fedora class is instantiated or after a :func:`reset` the instance can be configured
    with a custom path to the configuration file::

        fedora = Fedora(cfg_file="path/to/my_fedora.cfg")

    """
    _instance = None

    def __new__(cls, *args, cfg_file=None, **kwargs):
        if not cls._instance:
            LOG.info("Creating a new Fedora instance")
            cls._instance = super(Fedora, cls).__new__(cls)
            if cfg_file is None:
                cfg_file = os.path.join(os.path.expanduser("~"), CFG_FILE)
            if not os.path.exists(cfg_file):
                raise FedoraException("No configuration file found at %s" % cfg_file)
            with open(cfg_file) as cfg:
                line = cfg.readline()
            lspl = line.split(",")
            if len(lspl) < 4:
                raise FedoraException("Invalid configuration file at %s,"
                                      "\n\tfirst line of file should contain 'host,port,username,password'." % cfg_file)
            host, port, username, password = lspl
            if not host.startswith("http"):
                host = "http://" + host
            cls.url = host + ":" + str(port) + "/fedora"
            cls.session = requests.Session()
            cls.session.headers = {'User-Agent': 'Mozilla/5.0'}
            cls.session.auth = (username, password)
            LOG.info("Created session for %s" % cls.url)
            response = cls.session.get(cls.url)
            if response.status_code != requests.codes.ok:
                cls._instance = None
                raise FedoraException("Could not connect to %s" % cls.url)
            else:
                LOG.info("Connected to %s" % cls.url)
        return cls._instance

    @staticmethod
    def reset():
        Fedora._instance = None
        LOG.info("Fedora instance was reset")

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







