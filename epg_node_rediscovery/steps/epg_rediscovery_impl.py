from behave import step
from com_ericsson_do_auto_integration_scripts.EPG_ECM_REDISCOVERY import epg_discovery_workflow_deployment, \
    delete_epg_vapp_entry_cmdb, delete_epg_vapp_vnflcmdb, epg_list_discovery, epg_discover_vapp, \
    epg_discover_workflow_status


@step("I start the Scenario to Install VNFLCM discovery workflow for EPG")
def step_impl(context):
    epg_discovery_workflow_deployment()



@step("I start the Scenario to Delete the EPG vapp entry from cmdb in ECM")
def step_impl(context):
    delete_epg_vapp_entry_cmdb()



@step("I start the Scenario to Delete the EPG vapp entry from VNFLCM DB")
def step_impl(context):
    delete_epg_vapp_vnflcmdb()



@step("I start the Scenario to Query- API to see the list of Discovery For EPG")
def step_impl(context):
    epg_list_discovery()


@step("I start the Scenario to Discover vapp and ECM Order status check")
def step_impl(context):
    epg_discover_vapp()


@step("I start the Scenario to LCM workflow verification for Discovered EPG")
def step_impl(context):
    epg_discover_workflow_status()