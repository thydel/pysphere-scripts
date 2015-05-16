#!/usr/bin/env python

import sys
import argparse
import pprint

from pysphere import VIServer, VITask, VIProperty
from pysphere.resources import VimService_services as VI

parser = argparse.ArgumentParser(description='Relocate a VM to another DataStore')

help = {
    '-v': 'The vcenter host',
    '-u': 'The user account used to connect to vcenter',
    '-p': 'The user password used to connect to vcenter',
    '-t': 'Trace of connection to vcenter go to a file for debug',
    '-c': 'On what cluster to migrate the VM',
    '-H': 'On what host to migrate the VM',
    '-r': 'On what resource to migrate the VM',
    '-s': 'On what DataStore to relocate the VM',
    'vm_name': 'The name of the VM to migrate',
    }

parser.add_argument('-v', '--vcenter', default='vcenter2.admin.oxa.tld', help=help['-v'])
parser.add_argument('-u', '--vuser', default='epiconcept', help=help['-u'])
parser.add_argument('-p', '--vpass', required=True, help=help['-p'])
parser.add_argument('-t', '--trace', type=argparse.FileType('w'), help=help['-t'])
parser.add_argument('-c', '--cluster', default='cluster-01', help=help['-c'])
parser.add_argument('-H', '--host', default='epiconcept.infra.esx-03.adm', help=help['-H'])
parser.add_argument('-r', '--resource', default='/Resources', help=help['-r'])
parser.add_argument('-s', '--store', default='Production-04', help=help['-s'])
parser.add_argument('vm_name', help=help['vm_name'])

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

task = vm.relocate(datastore=ds_mor)

pprint.pprint(task)

server.disconnect()
