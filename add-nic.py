#!/usr/bin/env python

import sys
import re
import optparse

from pysphere import VIServer, VITask
from pysphere.resources import VimService_services as VI

parser = optparse.OptionParser()
parser.add_option('--name',type='string')
parser.add_option('--vcenter',type='string')
parser.add_option('--vuser',type='string')
parser.add_option('--vpass',type='string')
parser.add_option('--net',type='string')
options, args = parser.parse_args()

opt_name = options.name
opt_vcenter = options.vcenter
opt_vuser = options.vuser
opt_vpass = options.vpass
opt_net = options.net

argvs = sys.argv
argc = len(argvs)

if ( argc != 6):
        print "Usage : python tst.py --vcenter=<vCenter IP> --vuser=<user> --vpass=<password> \
	--name=<VM name> --net=<vlan label>"
        sys.exit(1)

# connect to vCenter
server = VIServer()
#server.connect(opt_vcenter, opt_vuser, opt_vpass, trace_file="debug.txt")
server.connect(opt_vcenter, opt_vuser, opt_vpass)

# specify the name of a  VM
vm = server.get_vm_by_name("%s" % opt_name)

request = VI.ReconfigVM_TaskRequestMsg()
_this = request.new__this(vm._mor)
_this.set_attribute_type(vm._mor.get_attribute_type())
request.set_element__this(_this)

spec = request.new_spec()

dev_change = spec.new_deviceChange()
dev_change.set_element_operation("add")

# We use a VMXNET3 controller here.  Introspect into
# VI.ns0 for all available controller names.
nic_ctlr = VI.ns0.VirtualVmxnet3_Def("nic_ctlr").pyclass()

nic_backing = VI.ns0.VirtualEthernetCardNetworkBackingInfo_Def("nic_backing").pyclass()
nic_backing.set_element_deviceName(opt_net)
nic_ctlr.set_element_addressType("generated")
nic_ctlr.set_element_backing(nic_backing)
nic_ctlr.set_element_key(4)
dev_change.set_element_device(nic_ctlr)

spec.set_element_deviceChange([dev_change])
request.set_element_spec(spec)

task = server._proxy.ReconfigVM_Task(request)._returnval
vi_task = VITask(task, server)

# Wait for task to finish
status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                 vi_task.STATE_ERROR])

if status == vi_task.STATE_ERROR:
    print "ERROR CONFIGURING VM:", vi_task.get_error_message()
else:
    print "VM CONFIGURED SUCCESSFULLY"

server.disconnect()
