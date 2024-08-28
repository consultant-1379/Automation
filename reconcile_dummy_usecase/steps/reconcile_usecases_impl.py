
from behave import *
from com_ericsson_do_auto_integration_scripts.DUMMY_RECONCILE_USECASES import *
from com_ericsson_do_auto_integration_scripts.RECONCILE_DUMMY_ECM_DEPLOYMENT import *

@step("I start the Scenario to Fetch VIM allocated quota details of tenant before reconcile")
def step_impl(context):
    fetch_allocated_quota_before()



@step("I start the Scenario to Fetch VM Vapp details before reconcile")
def step_impl(context):
    fetch_VM_Vapp_details_before()



@step("I start the Scenario to Create SRT for reconcile Vapp")
def step_impl(context):
    create_reconcile_srt()



@step("I start the Scenario to Register Valid 9M image for reconcile Vapp")
def step_impl(context):
    register_reconcile_image()
    


@step("I start the Scenario to Create Block storage volume for reconcile Vapp")
def step_impl(context):
    create_reconcile_block_storage()
    


@step("I start the Scenario to Run stack update command on openstack with stack update template uc-1")
def step_impl(context):
    stack_update_uc1()


@step("I start the Scenario to Perform reconcile usecase-1 on ECM")
def step_impl(context):
    reconcile_vapp()


@step("I start the Scenario to Fetch VIM allocated quota details of tenant after reconcile usecase-1")
def step_impl(context):
    fetch_allocated_quota_usecase1()



@step("I start the Scenario to Fetch VM Vapp details after reconcile usecase-1")
def step_impl(context):
    fetch_VM_Vapp_details_usecase1()




@step("I start the Scenario to Verification of reconcile usecase-1")
def step_impl(context):
    verification_reconcile_usecase1()


@step("I start the Scenario to Delete Resource from open stack")
def step_impl(context):
    delete_resource()


@step("I start the Scenario to Perform reconcile usecase-2")
def step_impl(context):
    reconcile_vapp()

@step("I start the Scenario to Fetch VM Vapp details after reconcile usecase-2")
def step_impl(context):
    fetch_VM_Vapp_details_usecase2()


@step("I start the Scenario to Verification of reconcile usecase-2")
def step_impl(context):
    verification_reconcile_usecase2()



@step("I start the Scenario to Create Block storage volume from openstack usecase-3")
def step_impl(context):
    create_openstack_srt()
    



@step("I start the Scenario to Create SRT from openstack usecase-3")
def step_impl(context):
    create_openstack_block_storage()
    
@step("I start the Scenario to Register SRT and BSV from openstack to EO-CM usecase-3")
def step_impl(context):
    register_srt_block_storage()

    
@step("I start the Scenario to Run stack update command on openstack with stack update template uc-3")
def step_impl(context):
    stack_update_uc3()
    

@step("I start the Scenario to Perform reconcile usecase-3")
def step_impl(context):
    reconcile_vapp()


@step("I start the Scenario to Fetch VIM allocated quota details of tenant after reconcile usecase-3")
def step_impl(context):
    fetch_allocated_quota_usecase3()



@step("I start the Scenario to Fetch VM Vapp details after reconcile usecase-3")
def step_impl(context):
    fetch_VM_Vapp_details_usecase3()
    
    
    
@step("I start the Scenario to Verification of reconcile usecase-3")
def step_impl(context):
    verification_reconcile_usecase3()    
