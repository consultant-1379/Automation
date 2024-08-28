
from behave import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_ETSI_TOSCA_NSD_DEPLOYMENT import *


@step("I start the Scenario to Update Onboard file for EPG package onboarding")
def step_impl(context):
    update_etsi_tosca_onboard_file()


@step("I start the Scenario to Start onboarding the EPG package")
def step_impl(context):
    onboard_epg_package()


@step("I start the Scenario to Verify onboarded EPG package")
def step_impl(context):
    verify_epg_package()
    

@step("I start the Scenario to Create ETSI TOSCA NSD package")
def step_impl(context):
    create_etsi_tosca_nsd_package()


@step("I start the Scenario to Upload ETSI TOSCA NSD package")
def step_impl(context):
    upload_etsi_tosca_nsd_package()


@step("I start the Scenario to Transfer So files to workflow pod")
def step_impl(context):
    epg_etsi_tosca_files_transfer()


@step("I start the Scenario to onboard the configuration templates for ETSI TOSCA NSD Package")
def step_impl(context):
    onboard_etsi_tosca_config_template()


@step("I start the Scenario to Onboard the ECM and ENM subsystems to SO")
def step_impl(context):
    onboard_etsi_node_subsytems()


@step("I start the Scenario to onboard service template for node deployment")
def step_impl(context):
    onboard_etsi_tosca_service_template()


@step("I start the Scenario to create the network service using serviceModel ID for Node deployment")
def step_impl(context):
    create_etsi_tosca_network_service()


@step("I start the Scenario to create NS")
def step_impl(context):
    create_etsi_tepg_ns()


@step("I start the Scenario to instantiate NS")
def step_impl(context):
    instantiate_etsi_tepg_ns()


@step("I start the Scenario of checking in SO for workflow deployment status")
def step_impl(context):
    check_epg_so_deploy_attribute()


@step("I start the Scenario of checking in SO for Node sync in ENM status")
def step_impl(context):
    check_epg_so_day1_configure_status()


@step("I start the Scenario of polling the state of network service using service ID for deployed node")
def step_impl(context):
    verify_node_service_status()


@step("I start the Scenario of checking LCM workflow")
def step_impl(context):
    check_epg_lcm_workflow_status()


@step("I start the Scenario of checking bulk configuration")
def step_impl(context):
    check_sol_epg_bulk_configuration()


@step("I start the Scenario of checking ECM order status")
def step_impl(context):
    check_epg_ecm_order()


@step("I start the Scenario of pinging the deployed Node")
def step_impl(context):
    check_etsi_tosca_epg_ip_ping_status()


@step("I start the Scenario of checking sync status of node in ENM")
def step_impl(context):
    check_epg_enm_sync_status()


@step("I start the Scenario of checking LCM workflow for etsi tosca EPG")
def step_impl(context):
    eocm_epg_etsi_tosca_lcm_workflow_status()


@step("I start the Scenario of checking ECM order status for etsi tosca EPG")
def step_impl(context):
    check_epg_ecm_order()


@step("I start the Scenario of checking sync status of epg etsi tosca in ENM")
def step_impl(context):
    eocm_epg_tosca_enm_sync_status()

