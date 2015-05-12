#!/usr/bin/env python

DATASTORE_NAME = 'Production-02'
UNIT_NUMBER = 2
DISK_SIZE_IN_GB = 30

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
parser.add_option('--dunit',type='string')
parser.add_option('--dsize',type='string')
options, args = parser.parse_args()

opt_name = options.name
opt_vcenter = options.vcenter
opt_vuser = options.vuser
opt_vpass = options.vpass
opt_dunit = options.dunit
opt_dsize = options.dsize

argvs = sys.argv
argc = len(argvs)

if (argc != 7):
        print "Usage : python {0} --vcenter=<vCenter IP> --vuser=<user> --vpass=<password> \
	--name=<VM name> --dsize=<disk size> --dunit=<disk unit>".format(sys.argv[0])
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

disk_spec = spec.new_deviceChange()
disk_spec.Operation = "add"
disk_spec.FileOperation = "create"

hd = VI.ns0.VirtualDisk_Def("hd").pyclass()
hd.Key = -100
hd.UnitNumber = int(opt_dunit)
hd.CapacityInKB = int(opt_dsize) * 1024 * 1024
hd.ControllerKey = 1000

backing = VI.ns0.VirtualDiskFlatVer2BackingInfo_Def("backing").pyclass()
data = vm.get_properties()
path = "%s" % data['path']
p = re.compile(r"\[([\w-]+)\] ")
try:
    m = p.match(path)
except re.error, e:
    print e
    sys.exit(1)
datastore_name = m.group(1)
backing.FileName = "[%s]" % datastore_name
backing.DiskMode = "persistent"
backing.Split = False
backing.WriteThrough = False
backing.ThinProvisioned = False
backing.EagerlyScrub = False
hd.Backing = backing

disk_spec.Device = hd

spec.DeviceChange = [disk_spec]
request.Spec = spec

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
