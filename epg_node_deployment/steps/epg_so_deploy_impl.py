from behave import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *


@step("I start the Scenario to Fetch NSD package from ECM to prepare ns1.yaml file")
def step_impl(context):
    fetch_node_nsd_package()
    


@step("I start the Scenario to Update NSD package and CSAR it")
def step_impl(context):
    update_node_nsd_template()


@step("I start the Scenario to Onboard the ECM and ENM subsystems to SO")
def step_impl(context):
    onboard_node_subsytems()   

@step("I start the Scenario to Start onboarding the NSD package")
def step_impl(context):
    onboard_node_nsd_template()

###########################################################################################################
############################## only needed in case of UDS ################################################
@step("I start the Scenario to Fetch out the service model Id")
def step_impl(context):
    fetch_service_model_id_uds()


@step("I start the Scenario to Create Network Service for EPG deployment using UDS")
def step_impl(context):
    create_epg_uds_so_network_service()

############################################################################################################
@step("I start the Scenario to onboard service template for node deployment")
def step_impl(context):
    onboard_node_service_template()
    

@step("I start the Scenario to create the network service using serviceModel ID for Node deployment")
def step_impl(context):
    create_node_network_service()
    


@step("I start the Scenario of checking in SO for workflow deployment status")
def step_impl(context):
    check_epg_so_deploy_attribute()


@step("I start the Scenario of checking in SO for Node sync in ENM status")
def step_impl(context):
    check_epg_so_day1_configure_status()


@step("I start the Scenario of polling the state of network service using service ID for deployed node")
def step_impl(context):
    verify_node_service_status()


@step("I start the Scenario of pinging the deployed Node")
def step_impl(context):
    check_epg_ip_ping_status()


@step("I start the Scenario of checking bulk configuration")
def step_impl(context):
    check_epg_bulk_configuration()

@step("I start the Scenario of checking LCM workflow")
def step_impl(context):
    check_epg_lcm_workflow_status()



@step("I start the Scenario of checking ECM order status")
def step_impl(context):
    check_epg_ecm_order()


@step("I start the Scenario of checking sync status of node in ENM")
def step_impl(context):
    check_epg_enm_sync_status()