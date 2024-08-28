from behave import *

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_scripts.VM_VNFM_LCM_ECM_INTEGRATION import *


log = Logger.get_logger('vm_vnfm_lcm_post_install_tasks_impl.py')



@step("I proceed to Register VM VNFM LCM")
def step_impl(context):
    register_vm_vnfm()


    

@step("I proceed to Add NFVO in VM VNFM LCM")
def step_impl(context):
    add_nfvo_vm_vnfm()




@step("I proceed to Add Default VIM to VM VNFM LCM")
def step_impl(context):
    add_vim_vm_vnfm()




@step("I proceed to deploy VM VNFM LCM workflow")
def step_impl(context):
    
    vm_vnfm_workflow_deployment()
    


@step("I start the Scenario to Update VM-VNFM OSS Password")
def step_impl(context):
    vm_vnfm_oss_password_update()
    



@step("I proceed to configure ENM on VM VNFM LCM")
def step_impl(context):
    enm_configuration_vm_vnfm()
    
