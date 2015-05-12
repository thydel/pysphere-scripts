#!/usr/bin/env python

import sys
import optparse
from pysphere import VIServer

parser = optparse.OptionParser()
parser.add_option('--prefix',type='string')
parser.add_option('--number',type='int')
parser.add_option('--template',type='string')
parser.add_option('--vcenter',type='string')
parser.add_option('--user',type='string')
parser.add_option('--password',type='string')
options, args = parser.parse_args()

opt_prefix = options.prefix
opt_number = options.number
opt_template = options.template
opt_vcenter = options.vcenter
opt_user = options.user
opt_password = options.password

argvs = sys.argv
argc = len(argvs)

if ( argc != 7):
        print "Usage : python clone_VMs_from_template_VM.py --vcenter=<vCenter IP> --user=<user> --password=<password>--prefix=<string> --number=<int> --template=<template VM name>"
        sys.exit(1)

# connect to vCenter
server = VIServer()
server.connect(opt_vcenter,opt_user,opt_password,trace_file="debug.txt")


resource_pools = server.get_resource_pools()
#print resource_pools

first_resource_pool = resource_pools.keys()[0]
#print first_resource_pool

# specify the full path of a template VM
template_vm = server.get_vm_by_name("%s" % opt_template)

i = 1
while i <= opt_number:
        new_vm = "%s-%s" % ( opt_prefix,i )
        clonedVM = template_vm.clone(new_vm,resourcepool=first_resource_pool)
        print "VM name : %s : status %s" % (clonedVM.get_property("name") , clonedVM.get_status())
        i += 1

server.disconnect()
        i += 1

server.disconnect()