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
                    help='Trace of connection to vcenter go to a file for debug')

parser.add_argument('-s', '--state', default='On',
                    help='List VM in state On or Off')

args = parser.parse_args()

kwargs = {};
if args.trace:
    kwargs['trace_file'] = args.trace.name

# connect to vCenter
server = VIServer()
server.connect(args.vcenter, args.vuser, args.vpass, **kwargs)

vmlist = server.get_registered_vms(status='powered' + args.state)

for vmpath in vmlist:
    vm = server.get_vm_by_path(vmpath)
    print vm.get_property('name')

server.disconnect()
