#! /usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import os

from fedora import utils
from fedora.rest.api import Fedora
from fedora.rest.ds import DatastreamProfile, FileItemMetadata


class Worker(object):
    """
    Do default chores with the fedora rest api.

    A worker reads and writes csv-files. The default dialect for such reading and writing is encapsulated in the
    class csv.excel. You can specify your own dialect by providing a class with the appropriate attributes.
    Example::

        class MyDialect(object):
            delimiter = ','
            quotechar = '"'
            escapechar = None
            doublequote = True
            skipinitialspace = False
            lineterminator = '\r\n'
            quoting = csv.QUOTE_MINIMAL

    """
    def __init__(self, dialect=csv.excel):
        self.fedora = Fedora()
        self.dialect = dialect

    def download_batch(self, id_list,
                       dump_dir="worker-downloads",
                       log_file="worker-log.csv",
                       id_in_path=True,
                       chunk_size=1024):
        """
        Download a bunch of files, store metadata in a work-log, compare checksums.

        :param id_list: either a list of file-id's or the name of the file that contains this list
        :param dump_dir: where to store downloaded files
        :param log_file: where to write the work-log
        :param dialect: what csv dialect should the work-log be written in, default: :class:`csv.excel`
        :param id_in_path: should (the number part of) the object_id be part of the local path, default: `True`
        :param chunk_size: size of chuncks for read-write operation, default: 1024
        :return: count of checksum errors
        """
        ds_id = "EASY_FILE"
        checksum_error_count = 0
        work_log = os.path.abspath(log_file)
        os.makedirs(os.path.dirname(work_log), exist_ok=True)
        with open(work_log, 'w', newline='') as csv_log:
            csv_writer = csv.writer(csv_log, dialect=self.dialect)
            csv_writer.writerow(["object_id", "ds_id", "server_date", "filename", "path", "local_path",
                                 "media_type", "size",
                                 "checksum_type", "checksum", "creation_date",
                                 "creator_role", "visible_to", "accessible_to",
                                 "checksum_error"])

            for object_id in self.id_iter(id_list):
                meta = self.fedora.download(object_id, ds_id, dump_dir, id_in_path, chunk_size)
                profile = DatastreamProfile(object_id, ds_id)
                profile.fetch()
                fmd = FileItemMetadata(object_id)
                fmd.fetch()
                server_date = utils.as_w3c_datetime(meta["Date"])
                filename = meta["filename"]
                local_path = meta["local-path"]
                media_type = meta["Content-Type"]
                size = int(meta["Content-Length"])

                sha1 = utils.sha1_for_file(local_path)
                if sha1 != profile.ds_checksum:
                    checksum_error = sha1
                    checksum_error_count += 1
                else:
                    checksum_error = ""

                csv_writer.writerow([object_id, ds_id, server_date, filename, fmd.fmd_path, local_path,
                                     media_type, size,
                                     profile.ds_checksum_type, profile.ds_checksum, profile.ds_creation_date,
                                     fmd.fmd_creator_role, fmd.fmd_visible_to, fmd.fmd_accessible_to,
                                     checksum_error])
        return checksum_error_count

    @staticmethod
    def id_iter(id_list):
        if isinstance(id_list, str):
            with open(id_list, "r") as id_file:
                for line in id_file:
                    yield line.rstrip()
        elif isinstance(id_list, list):
            for id in id_list:
                yield id