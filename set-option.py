#!/usr/bin/env python

DATASTORE_NAME = 'Production-02'

import sys
import optparse

from pysphere import VIServer

parser = optparse.OptionParser()
parser.add_option('--vcenter',type='string')
parser.add_option('--vuser',type='string')
parser.add_option('--vpass',type='string')
parser.add_option('--name',type='string')

parser.add_option('--var',type='string')
parser.add_option('--val',type='string')

options, args = parser.parse_args()

opt_vcenter = options.vcenter
opt_vuser = options.vuser
opt_vpass = options.vpass
opt_name = options.name

opt_var = options.var
opt_val = options.val

argvs = sys.argv
argc = len(argvs)

if ( argc != 7):
        print "Usage : python tst.py --vcenter=<vCenter IP> --vuser=<user> --vpass=<password> \
	--name=<VM name> --var=<var> --val=<val>"
        sys.exit(1)

# connect to vCenter
server = VIServer()
#server.connect(opt_vcenter, opt_vuser, opt_vpass, trace_file="debug.txt")
server.connect(opt_vcenter, opt_vuser, opt_vpass)

#path_to_vm = "[%s] %/%s.vmx" % (datastore_name, opt_name, opt_name)
path_to_vm = "[%s] %s/%s.vmx" % (DATASTORE_NAME, opt_name, opt_name)

vm = server.get_vm_by_path(path_to_vm)

#disk.locking = "FALSE"
#disk.EnableUUID = "TRUE"
#settings = { 'disk.locking': 'FALSE' }
#settings = { 'disk.EnableUUID': 'TRUE' }

settings = { opt_var: opt_val }

#print settings

vm.set_extra_config(settings)

server.disconnect()
