#!/usr/bin/env python

import sys
import argparse
import pprint

from pysphere import VIServer, VITask, VIProperty
from pysphere.resources import VimService_services as VI

parser = argparse.ArgumentParser(description='Show VM propertie')

# vsphere.admin.oxa.tld
parser.add_argument('-v', '--vcenter', default='vcenter2.admin.oxa.tld',
                    help='The vcenter host')

parser.add_argument('-u', '--vuser', default='epiconcept',
                    help='The user account used to connect to vcenter')

parser.add_argument('-p', '--vpass', required=True,
                    help='The user password used to connect to vcenter')

parser.add_argument('-t', '--trace', type=argparse.FileType('w'),
                    help='Trace of connection to vcenter go to a file for debug')

parser.add_argument('-c', '--cluster', default='cluster-01',
                    help='On what cluster to migrate the VM')

parser.add_argument('-s', '--state', default='On',
                    help='List VM in state On or Off')

parser.add_argument('-H', '--hosts', action='store_true', help='Show host')
parser.add_argument('-D', '--datastores', action='store_true', help='Show Datastore')

args = parser.parse_args()

kwargs = {};
if args.trace:
    kwargs['trace_file'] = args.trace.name

# connect to vCenter
server = VIServer()
server.connect(args.vcenter, args.vuser, args.vpass, **kwargs)

def invert(d): return dict(zip(d.values(), d.keys()))
def getClusterByName(server, name): return invert(server.get_clusters()).get(name, None)
cluster_mor = getClusterByName(server, args.cluster)

vmlist = server.get_registered_vms(cluster=cluster_mor, status='powered' + args.state)

# https://groups.google.com/forum/#!topic/pysphere/UCL7epa_sFU
hosts = server.get_hosts()

for vmpath in vmlist:
    vm = server.get_vm_by_path(vmpath)
    host_mor = vm.properties.runtime.host._obj
    # print vm.properties.runtime.host.name
    if args.hosts:
        print vm.get_property('name'), hosts[host_mor]
    elif args.datastores:
        print vm.get_property('name'), vm.properties.datastore[0].name
    else:
        print vm.get_property('name')

server.disconnect()
