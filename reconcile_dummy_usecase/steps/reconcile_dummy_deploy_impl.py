
from behave import *

from com_ericsson_do_auto_integration_scripts.RECONCILE_DUMMY_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.DUMMY_RECONCILE_USECASES import *

@step("I start the Scenario to Delete Reconcile Block Storage Volume")
def step_impl(context):
    delete_reconcile_volumes()


@step("I start the Scenario to Update the hot yaml file")
def step_impl(context):
    update_reconcile_hot_yaml()



@step("I start the Scenario to Update the VNFD wrapper file")
def step_impl(context):
    update_reconcile_vnfd_wrapper()
    


@step("I start the Scenario to Transfer reconcile vnflaf package to VNF-LCM")
def step_impl(context):
    transfer_reconcile_vnflaf_package()
    


@step("I start the Scenario to Update Onboard file for reconcile dummy VNF")
def step_impl(context):
    update_reconcile_dummy_onboard_file()


@step("I start the Scenario to Start onboarding the reconcile dummy VNF package")
def step_impl(context):
    reconcile_onboard_dummy_package()
    

@step("I start the Scenario to Verify onboarded reconcile dummy VNF package")
def step_impl(context):
    verify_reconcile_dummy_package()
    

@step("I start the Scenario to Update deploy file for reconcile dummy VNF package")
def step_impl(context):
    update_reconcile_dummy_deploy_file()
    

@step("I start the Scenario to Start deploying the reconcile dummy VNF package")
def step_impl(context):
    deploy_reconcile_dummy_package()


@step("I start the Scenario to Verify deployed reconcile dummy VNF package")
def step_impl(context):
    verify_reconcile_dummy_deployment()
    
    
@step("I start the Scenario to List Vapp and Vim details")
def step_impl(context):
    fetch_vapp_vim_details('before')
      
