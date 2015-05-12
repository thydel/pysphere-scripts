#!/usr/bin/env python

import sys
import argparse
import pprint

from pysphere import VIServer, VITask, VIProperty
from pysphere.resources import VimService_services as VI

parser = argparse.ArgumentParser(description='Show VM propertie')

parser.add_argument('-v', '--vcenter', default='vsphere.admin.oxa.tld',
                    help='The vcenter host')

parser.add_argument('-u', '--vuser', default='epiconcept',
                    help='The user account used to connect to vcenter')

parser.add_argument('-p', '--vpass', required=True,
                    help='The user password used to connect to vcenter')

parser.add_argument('-t', '--trace', type=argparse.FileType('w'),
                    help='trace of connection to vcenter go to a file for debug')

parser.add_argument('-d', '--devices', action='store_true',
                    help='Do not remove devices from property')

parser.add_argument('-f', '--files', action='store_true',
                    help='Do not remove files from property')

parser.add_argument('vm_name',
                    help='The name of the VM')

args = parser.parse_args()

kwargs = {};
if args.trace:
    kwargs['trace_file'] = args.trace.name

# connect to vCenter
server = VIServer()
server.connect(args.vcenter, args.vuser, args.vpass, **kwargs)

# specify the name of a  VM
vm = server.get_vm_by_name(args.vm_name)

data = vm.get_properties()

if not args.devices: del data['devices']
if not args.files: del data['files']

pprint.pprint(data)

server.disconnect()
