
from com_ericsson_do_auto_integration_scripts.VM_VNFM_LCM_ECM_INTEGRATION import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_register_vm_vnfm():
    """
    This method is used to Register VM VNFM LCM
    """
    register_vm_vnfm()


def test_add_nfvo_vm_vnfm():
    """
    This method is used to Add NFVO in VM VNFM LCM
    """
    add_nfvo_vm_vnfm()


def test_add_vim_vm_vnfm():
    """
    This method is used to Add Default VIM to VM VNFM LCM
    """
    add_vim_vm_vnfm()


def test_vm_vnfm_workflow_deployment():
    """
    This method is used to deploy VM VNFM LCM workflow
    """
    vm_vnfm_workflow_deployment()



def test_vm_vnfm_oss_password_update():
    """
    This method is used to Update VM-VNFM OSS Password
    """
    vm_vnfm_oss_password_update()


def test_enm_configuration_vm_vnfm():
    """
    This method is used to configure ENM on VM VNFM LCM
    """
    enm_configuration_vm_vnfm()

