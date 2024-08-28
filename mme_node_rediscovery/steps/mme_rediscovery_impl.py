from behave import *
from com_ericsson_do_auto_integration_scripts.MME_ECM_REDISCOVERY import *



@step("I start the Scenario to Install VNFLCM discovery workflow for MME")
def step_impl(context):
    MME_discovery_workflow_deployment()



@step("I start the Scenario to Delete the MME vapp entry from cmdb in ECM")
def step_impl(context):
    delete_MME_vapp_entry_cmdb()



@step("I start the Scenario to Delete the MME vapp entry from VNFLCM DB")
def step_impl(context):
    delete_MME_vapp_vnflcmdb()



@step("I start the Scenario to Query- API to see the list of Discovery For MME")
def step_impl(context):
    MME_list_discovery()


@step("I start the Scenario to Discover vapp and ECM order status check for MME")
def step_impl(context):
    MME_discover_vapp()


@step("I start the Scenario to LCM workflow verification for Discovered MME")
def step_impl(context):
    MME_discover_workflow_status()