#!/usr/bin/env python

import sys
import argparse
import pprint

from pysphere import VIServer, VITask, VIProperty
from pysphere.resources import VimService_services as VI

parser = argparse.ArgumentParser(description='Migrate a VM to another host')

#vsphere.admin.oxa.tld
parser.add_argument('-v', '--vcenter', default='vcenter2.admin.oxa.tld',
                    help='The vcenter host')

parser.add_argument('-u', '--vuser', default='epiconcept',
                    help='The user account used to connect to vcenter')

parser.add_argument('-p', '--vpass', required=True,
                    help='The user password used to connect to vcenter')

parser.add_argument('-t', '--trace', type=argparse.FileType('w'),
                    help='trace of connection to vcenter go to a file for debug')

parser.add_argument('-c', '--cluster', default='cluster-01',
                    help='On what cluster to migrate the VM')

parser.add_argument('-H', '--host', default='epiconcept.infra.esx-03.adm',
                    help='On what host to migrate the VM')

parser.add_argument('-r', '--resource', default='/Resources',
                    help='On what resource to migrate the VM')

parser.add_argument('-s', '--store', default='Production-04',
                    help='On what DataStore to relocate the VM')

parser.add_argument('vm_name',
                    help='The name of the VM to migrate')

args = parser.parse_args()

kwargs = {};
if args.trace:
    kwargs['trace_file'] = args.trace.name

# connect to vCenter
server = VIServer()
server.connect(args.vcenter, args.vuser, args.vpass, **kwargs)

# specify the name of a  VM
vm = server.get_vm_by_name(args.vm_name)

################
# https://code.google.com/p/pysphere/issues/detail?id=52
def getHostByName(server, name):
    mor = None
    for host_mor, host_name in server.get_hosts().items():
        if host_name == name: mor = host_mor; break
    return mor

def getResourcePoolByName(server, resourcepool):
    mor = None
    for rp_mor, rp_path in server.get_resource_pools().items():
        if resourcepool in rp_path : mor = rp_mor; break
    return mor

def getDatastoreByName(server, name):
    mor = None
    for ds_mor, ds_path in server.get_datastores().items():
        if ds_path == name: mor = ds_mor; break
    return mor
################

def getResourcePoolByNameFromCluster(server, cluster, resourcepool):
    mor = None
    for rp_mor, rp_path in server.get_resource_pools(cluster).items():
        if resourcepool in rp_path : mor = rp_mor; break
    return mor

#def invert(d, v): return dict(map(lambda (k, v): (v, k), d.items()))
def invert(d): return dict(zip(d.values(), d.keys()))

def getClusterByName(server, name): return invert(server.get_clusters()).get(name, None)

host_mor = getHostByName(server, args.host)
#print(host_mor)

# https://github.com/morphizer/misc/tree/master/python/pysphere
cluster_mor = getClusterByName(server, args.cluster)
#print(cluster_mor)

rp_mor = getResourcePoolByNameFromCluster(server, cluster_mor, args.resource)
#print(rp_mor)

ds_mor = getDatastoreByName(server, args.store)
#print(ds_mor)

task = vm.migrate(resource_pool=rp_mor, host=host_mor)

pprint.pprint(task)

server.disconnect()
