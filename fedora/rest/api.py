#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os
import re
import urllib.parse

import requests

LOG = logging.getLogger(__name__)
CFG_FILE = "src/fedora.cfg"

FEDORA_INSTANCE = None


class FedoraException(RuntimeError):
    pass


class Fedora(object):
    """


    """

    def __init__(self, host, port, username, password):
        if not host.startswith("http"):
            host = "http://" + host
        self.url = host + ":" + str(port) + "/fedora"
        self.session = requests.Session()
        self.session.headers = {'User-Agent': 'Mozilla/5.0'}
        self.session.auth = (username, password)
        response = self.session.get(self.url)
        if response.status_code != requests.codes.ok:
            raise FedoraException("Could not connect to %s" % self.url)
        else:
            LOG.info("Connected to %s\n" % self.url)
            print('Version: 1.0.3 Connected to %s, logged in as %s\n' % (self.url, username))

    @staticmethod
    def from_file(cfg_file=None):
        if cfg_file is None:
            cfg_file = os.path.join(os.path.expanduser("~"), CFG_FILE)
        LOG.info("Creating a new Fedora instance from file %s" % cfg_file)
        with open(cfg_file) as cfg:
            line = cfg.readline().strip()
        host, port, username, password = line.split(",")
        return Fedora(host, port, username, password)

    def as_text(self, url):
        response = self.session.get(url)
        if response.status_code == requests.codes.ok:
            text = str(response.content, 'utf-8', errors='replace')
            return text
        else:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))

    def object_xml(self, object_id):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-getObjectXML

        auth required
        """
        url = self.url + "/objects/" + object_id + "/objectXML"
        return self.as_text(url)

    def datastream(self, object_id, ds_id, content_format="content"):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-getDatastream

        auth required for some datastreams
        """
        if content_format == "content":
            postfix = "/content"
        else:
            postfix = "?format=" + content_format
        url = self.url + "/objects/" + object_id + "/datastreams/" + ds_id + postfix
        return self.as_text(url)

    def add_managed_datastream(self, pid, ds_id, ds_label, filepath, mediatype, sha1):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-addDatastream

        /objects/{pid}/datastreams/{dsID} ? [controlGroup] [dsLocation] [altIDs] [dsLabel] [versionable] [dsState] [formatURI] [checksumType] [checksum] [mimeType] [logMessage]

        """
        url = self.url + '/objects/' + pid + '/datastreams/' + ds_id
        payload = {'controlGroup': 'M', 'dsLabel': ds_label, 'checksumType': 'SHA-1', 'checksum': sha1, 'mimeType': mediatype}
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as file:
            files = {'file': (filename, file, mediatype, {'Expires': '0'})}
            response = self.session.post(url, params=payload, files=files)
            if response.status_code != 201:
                raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))
        return response

    def modify_datastream(self, pid, ds_id, ds_label, filepath, mediatype, formatURI, logMessage):
        """
        See: https://wiki.duraspace.org/display/FEDORA36/REST+API#RESTAPI-modifyDatastream

        /objects/{pid}/datastreams/{dsID} ? [dsLocation] [altIDs] [dsLabel] [versionable] [dsState] [formatURI] [checksumType] [checksum] [mimeType] [logMessage] [ignoreContent] [lastModifiedDate]

        :return: datastream profile
        """
        url = self.url + '/objects/' + pid + '/datastreams/' + ds_id
        payload = {'dsLabel': ds_label, 'checksumType': 'SHA-1', # fedora computes another checksum 'checksum': sha1,
                   'mimeType': mediatype, 'formatURI': formatURI, 'logMessage': logMessage}
        filename = os.path.basename(filepath)
        with open(filepath, 'rb') as file:
            response = self.session.put(url, params=payload, data=file)
            if response.status_code != 200:
                raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))
        return response

    def list_datastreams(self, pid):
        """
        /objects/{pid}/datastreams ? [format] [asOfDateTime]
        """
        url = self.url + '/objects/' + pid + '/datastreams'
        payload = {'format': 'xml'}
        response = self.session.get(url, params=payload)
        if response.status_code != 200:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))
        return response.text

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

    def download(self, object_id, ds_id, folder="downloads", id_in_path=True, chunk_size=1024):
        """
        Download datastream contents from Fedora.

        :param object_id: id of the digital object
        :param ds_id: id of the datastream within this digital object
        :param folder: where to store the downloaded file, default: 'downloads'
        :param id_in_path: should a subdirectory be created within the the download folder
        :param chunk_size: chunk size for read/write operation
        :return: dict with response headers + filename and local_path of the downloaded file
        """
        if id_in_path:
            path = os.path.abspath(os.path.join(folder, object_id.split(":")[1]))
        else:
            path = os.path.abspath(folder)
        os.makedirs(path, exist_ok=True)
        url = self.url + "/objects/" + object_id + "/datastreams/" + ds_id + "/content"
        response = self.session.get(url, stream=True)
        if response.status_code == requests.codes.ok:
            filename = self.compute_filename(response)
            local_path = os.path.join(path, filename)
            with open(local_path, 'wb') as fd:
                for chunk in response.iter_content(chunk_size):
                    fd.write(chunk)
            LOG.debug("Downloaded %s" % local_path)
            meta = {"filename": filename, "local-path": local_path}
            meta.update(response.headers)
            return meta
        else:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))

    @staticmethod
    def compute_filename(response):
        filename = "unknown"
        # # Fedora response header has filenames with double extensions like "filename.pdf.pdf", "db.mdb.bin"
        # # therefore this code is problematic
        cd = response.headers['content-disposition']
        fn = re.findall("filename=(.+)", cd)
        if len(fn) > 0:
            filename = fn[0]
            if filename.startswith("\""):
                filename = filename[1:]
            if filename.endswith("\""):
                filename = filename[:-1]
        # # correct double extension
        exts = filename.split(".")
        leng = len(exts)
        if leng > 2:
            filename = ".".join(exts[:-1])
        return filename

    def find_objects(self, query, max_results=25, result_format="xml", fields=("pid", "label")):
        """
        See: https://wiki.duraspace.org/display/FEDORA38/REST+API#RESTAPI-findObjects

        /objects?query=pid%7E*1&maxResults=50&format=true&pid=true&title=true

        """
        parameters = {"query": query, "maxResults": max_results, "resultFormat": result_format}
        for field in fields:
            parameters.update({field: "true"})

        url = self.url + "/objects?" + urllib.parse.urlencode(parameters)
        return self.as_text(url)

    def risearch(self, query, type="tuples", flush=False, lang="sparql", format="CSV", limit=1000, distinct="off",
                 stream="on"):
        """
        See: https://wiki.duraspace.org/display/FEDORA38/Resource+Index+Search#ResourceIndexSearch-ApplicationInterfaceapp

        risearch?type=tuples&flush=[*true* (default is false)]
                                     &lang=*itql|sparql*
                                     &format=*CSV|Simple|Sparql|TSV*
                                     &limit=[*1* (default is no limit)]
                                     &distinct=[*on* (default is off)]
                                     &stream=[*on* (default is off)]
                                     &query=*QUERY_TEXT_OR_URL*
        """

        data = {"type": type, "flush": str(flush).lower(), "lang": lang, "format": format, "limit": limit,
                "distinct": distinct, "query": query}
        url = self.url + "/risearch"
        response = self.session.post(url, data)
        if response.status_code != requests.codes.ok:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))

        return response.text

    def ingest(self, pid=None, label=None, format=None, encoding=None, namespace=None, owner_id=None, log_message=None,
               ignore_mime=False):
        """
        See: https://wiki.duraspace.org/display/FEDORA38/REST+API#RESTAPI-ingest

        /objects/ [{pid}| new] ? [label] [format] [encoding] [namespace] [ownerId] [logMessage] [ignoreMime]

        POST: /objects/new?namespace=demo
        POST: /objects/test:100?label=Test
        :return: the PID of the newly ingested object
        """
        query = {'label': label, 'format': format, 'encoding': encoding, 'namespace': namespace, 'ownerId': owner_id,
                 'logMessage': log_message, 'ignoreMime': ignore_mime}
        query = {k:v for k, v in query.items() if v is not None}

        npid = pid if pid else 'new'
        url = self.url + "/objects/" + npid + "?" + urllib.parse.urlencode(query)
        response = self.session.post(url);
        if response.status_code != requests.codes.created:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))
        return response.text

    def get_next_pid(self, num_pids=1, namespace='test', format='xml'):
        """
        See: https://wiki.duraspace.org/display/FEDORA38/REST+API#RESTAPI-getNextPID

        /objects/nextPID ? [numPIDs] [namespace] [format]
        POST: /objects/nextPID?numPIDs=5&namespace=test&format=xml
        :return: next PIDs in either xml or html
        """
        query = {'numPIDs': num_pids, 'namespace': namespace, 'format': format}
        url = self.url + "/objects/nextPID?" + urllib.parse.urlencode(query)
        response = self.session.post(url);
        if response.status_code != requests.codes.ok:
            raise FedoraException("Error response from Fedora: %d %s" % (response.status_code, response.reason))
        return response.text

## See static method Fedora.from_file()
# def instance(cfg_file=None) -> Fedora:
#     global FEDORA_INSTANCE
#     if FEDORA_INSTANCE is None:
#         FEDORA_INSTANCE = _create_instance(cfg_file)
#     return FEDORA_INSTANCE
#
#
# def reset_instance():
#     global FEDORA_INSTANCE
#     FEDORA_INSTANCE = None
#
#
# def _create_instance(cfg_file) -> Fedora:
#     if cfg_file is None:
#         cfg_file = os.path.join(os.path.expanduser("~"), CFG_FILE)
#     if not os.path.exists(cfg_file):
#         raise FedoraException('The configuration file {} does noet exist'.format(cfg_file))
#
#     with open(cfg_file) as cfg:
#         line = cfg.readline().strip()
#
#     lspl = line.split(",")
#     if len(lspl) < 4:
#         raise FedoraException("Invalid configuration file at {},"
#                               "\n\tfirst line of file should contain 'host,port,username,password'."
#                               .format(cfg_file))
#     host, port, username, password = lspl
#     if not host.startswith("http"):
#         host = "http://" + host
#     return Fedora(host, port, username, password)
