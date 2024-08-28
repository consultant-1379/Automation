
from behave import *

from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *


@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):    
    remove_host_lcm_entry()

    

@step("I start the Scenario to Add admin and heat_stack_owner roles to project user")
def step_impl(context):
    update_admin_heatstack_rights()
   
        

@step("I start the Scenario to Update VNFLCM OSS Password")
def step_impl(context):
    update_lcm_oss_password()

   

    
@step("I start the Scenario to Install the workflow on VNF-LCM")
def step_impl(context):    
    ims_workflow_deployment()
    
