#!/usr/bin/env python

import sys
import argparse
import datetime

from pysphere import VIServer, VITask, VIProperty
from pysphere.resources import VimService_services as VI

parser = argparse.ArgumentParser(description='List files on a DataStore')

class option(object): pass

vcenter = option()
vcenter.default = 'vsphere.admin.oxa.tld'
vcenter.help = 'The vcenter host (default "{}")'.format(vcenter.default)
parser.add_argument('--vcenter', metavar='HOST', default=vcenter.default, help=vcenter.help)

user = option()
user.default = 'epiconcept'
user.help = 'The user account used to connect to vcenter (default "{}")'.format(user.default)
parser.add_argument('--user', default=user.default, help=user.help)

parser.add_argument('-p', dest='password', required=True,
                    help='The user password used to connect to vcenter')

parser.add_argument('--trace', metavar='FILENAME', type=argparse.FileType('w'),
                    help='trace of connection to vcenter go to a file for debug')

store = lambda: 'Production-02'
store.help = 'The DataStore to use (default "{}")'.format(store())
store.choices = ['Production', 'Production-02', 'Preproduction']
parser.add_argument('-s', dest='store', choices=store.choices, default=store(),
                    help=store.help)

parser.add_argument('-b', '--byte', action='store_true',
                    help='Show byte insteas of human readable file size')

parser.add_argument('path', default='/', nargs='?',
                    help='The path on the DataStore (default /)')

parser.add_argument('-m', dest='match', metavar='GLOB', nargs='*', default=[],
                    help='A list of pattern matching file names (e.g "*.vmdk", "*.vmx", "*.log")')

args = parser.parse_args()

# https://groups.google.com/forum/#!topic/pysphere/2jN7rr-tZ04
def get_file_list(datastore, path="/", case_insensitive=True, folders_first=True, match_patterns=[]):

    ds = [k for k,v in server.get_datastores().items() if v == datastore][0]
    ds_browser = VIProperty(server, ds).browser._obj

    request = VI.SearchDatastore_TaskRequestMsg()
    _this = request.new__this(ds_browser)
    _this.set_attribute_type(ds_browser.get_attribute_type())
    request.set_element__this(_this)
    request.set_element_datastorePath("[%s] %s" % (datastore, path))

    search_spec = request.new_searchSpec()

    query = [VI.ns0.FloppyImageFileQuery_Def('floppy').pyclass(),
             VI.ns0.FolderFileQuery_Def('folder').pyclass(),
             VI.ns0.IsoImageFileQuery_Def('iso').pyclass(),
             VI.ns0.VmConfigFileQuery_Def('vm').pyclass(),
             VI.ns0.TemplateConfigFileQuery_Def('template').pyclass(),
             VI.ns0.VmDiskFileQuery_Def('vm_disk').pyclass(),
             VI.ns0.VmLogFileQuery_Def('vm_log').pyclass(),
             VI.ns0.VmNvramFileQuery_Def('vm_ram').pyclass(),
             VI.ns0.VmSnapshotFileQuery_Def('vm_snapshot').pyclass()]
    search_spec.set_element_query(query)
    details = search_spec.new_details()
    details.set_element_fileOwner(True)
    details.set_element_fileSize(True)
    details.set_element_fileType(True)
    details.set_element_modification(True)
    search_spec.set_element_details(details)
    search_spec.set_element_searchCaseInsensitive(case_insensitive)
    search_spec.set_element_sortFoldersFirst(folders_first)
    search_spec.set_element_matchPattern(match_patterns)
    request.set_element_searchSpec(search_spec)
    response = server._proxy.SearchDatastore_Task(request)._returnval
    task = VITask(response, server)
    if task.wait_for_state([task.STATE_ERROR, task.STATE_SUCCESS]) == task.STATE_ERROR:
        raise Exception(task.get_error_message())

    info = task.get_result()

    if not hasattr(info, "file"):
        return []
    return [{'path':fi.path,
             'size':fi.fileSize,
             'modified':fi.modification,
             'owner':fi.owner
            } for fi in info.file]

# http://stackoverflow.com/questions/1094841/reusable-library-to-get-human-readable-version-of-file-size
def human_readable_data_quantity(quantity, multiple=1024):
    if quantity == 0:
        quantity = +0
    SUFFIXES = ["B"] + [i + {1000: "B", 1024: "iB"}[multiple] for i in "KMGTPEZY"]
    for suffix in SUFFIXES:
        if quantity < multiple or suffix == SUFFIXES[-1]:
            if suffix == SUFFIXES[0]:
                return "%d%s" % (quantity, suffix)
            else:
                return "%.1f%s" % (quantity, suffix)
        else:
            quantity /= multiple

kwargs = {};
if args.trace:
    kwargs['trace_file'] = args.trace.name

# connect to vCenter
server = VIServer()
server.connect(args.vcenter, args.user, args.password, **kwargs)

kwargs = { 'match_patterns': args.match };
list = get_file_list(args.store, args.path, **kwargs)

for file in list:
    date = '{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime(*file['modified'][0:6]))
    size = file['size'] if args.byte else human_readable_data_quantity(file['size'])
    print '{} {} {}'.format(file['path'], size, date)

server.disconnect()
