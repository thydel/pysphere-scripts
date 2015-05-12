# http://snapfiber.com/pysphere-missing-pieces.html

from pysphere.resources import VimService_services as VI

def add_nic(vm, vcenter, net_label="DEFAULT_LABEL"):
''' Adds a NIC to the host.  Returns a VITask object.
    @vm: A VIVirtualMachine object.
    @vcenter: An authenticated VIServer object.
    @net_label: The network label to apply to the NIC.
    '''

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
    nic_backing.set_element_deviceName(net_label)
    nic_ctlr.set_element_addressType("generated")
    nic_ctlr.set_element_backing(nic_backing)
    nic_ctlr.set_element_key(4)
    dev_change.set_element_device(nic_ctlr)

    spec.set_element_deviceChange([dev_change])
    request.set_element_spec(spec)
    vcenter._proxy.ReconfigVM_Task(request)
