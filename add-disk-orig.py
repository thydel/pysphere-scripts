HOST = "virtualcenter.com"
USER = "root"
PASSWORD = "secret"

DATASTORE_NAME = "datastore1" #WHERE THE DISK WILL BE CREATED AT
DISK_SIZE_IN_MB = 500
VM_PATH = "[datastore1] path/to/the/config/file.vmx"
UNIT_NUMBER = 1

from pysphere import VIServer, VITask
from pysphere.resources import VimService_services as VI

s = VIServer()
s.connect(HOST, USER, PASSWORD)

vm = s.get_vm_by_path(VM_PATH)

request = VI.ReconfigVM_TaskRequestMsg()
_this = request.new__this(vm._mor)
_this.set_attribute_type(vm._mor.get_attribute_type())
request.set_element__this(_this)
    
spec = request.new_spec()

dc = spec.new_deviceChange()
dc.Operation = "add"
dc.FileOperation = "create"

hd = VI.ns0.VirtualDisk_Def("hd").pyclass()
hd.Key = -100
hd.UnitNumber = UNIT_NUMBER
hd.CapacityInKB = DISK_SIZE_IN_MB * 1024
hd.ControllerKey = 1000

backing = VI.ns0.VirtualDiskFlatVer2BackingInfo_Def("backing").pyclass()
backing.FileName = "[%s]" % DATASTORE_NAME
backing.DiskMode = "persistent"
backing.Split = False
backing.WriteThrough = False
backing.ThinProvisioned = False
backing.EagerlyScrub = False
hd.Backing = backing

dc.Device = hd

spec.DeviceChange = [dc]
request.Spec = spec

task = s._proxy.ReconfigVM_Task(request)._returnval
vi_task = VITask(task, s)

# Wait for task to finish
status = vi_task.wait_for_state([vi_task.STATE_SUCCESS,
                                 vi_task.STATE_ERROR])

if status == vi_task.STATE_ERROR:
    print "ERROR CONFIGURING VM:", vi_task.get_error_message()
else:
    print "VM CONFIGURED SUCCESSFULLY"

s.disconnect()
