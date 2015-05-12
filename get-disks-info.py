#!/usr/bin/env python

import sys
import optparse

from pysphere import VIServer

parser = optparse.OptionParser()

parser.add_option('--name',type='string')
parser.add_option('--vcenter',type='string')
parser.add_option('--vuser',type='string')
parser.add_option('--vpass',type='string')

options, args = parser.parse_args()

opt_name = options.name
opt_vcenter = options.vcenter
opt_vuser = options.vuser
opt_vpass = options.vpass

usage = "Usage : python {0} --vcenter=<vCenter_IP> --vuser=<user> --vpass=<password> --name=<VM_name>"

if (len(sys.argv) != 5):
        print usage.format(sys.argv[0])
        sys.exit(1)

# connect to vCenter
server = VIServer()
#server.connect(opt_vcenter, opt_vuser, opt_vpass, trace_file="debug.txt")
server.connect(opt_vcenter, opt_vuser, opt_vpass)

# specify the name of a  VM
vm = server.get_vm_by_name("%s" % opt_name)

disks = [d for d in vm.properties.config.hardware.device
         if d._type=='VirtualDisk'
         and d.backing._type in ['VirtualDiskFlatVer1BackingInfo',
                                 'VirtualDiskFlatVer2BackingInfo',
                                 'VirtualDiskRawDiskMappingVer1BackingInfo',
                                 'VirtualDiskSparseVer1BackingInfo',
                                 'VirtualDiskSparseVer2BackingInfo'
                                 ]]

for disk in disks:
    print "Label:", disk.deviceInfo.label
    print "Summary:", disk.deviceInfo.summary
    print "Disk Mode:", disk.backing.diskMode #e.g. persistent, independent
    print "Disk type:", disk.backing._type #e.g. VirtualDiskRawDiskMappingVer1BackingInfo
    if hasattr(disk.backing, "thinProvisioned"):
        print "Thin provisioned:", disk.backing.thinProvisioned

    print "Unit Number:", disk.unitNumber
    print "Key:", disk.key
    print "File Name:", disk.backing.fileName

