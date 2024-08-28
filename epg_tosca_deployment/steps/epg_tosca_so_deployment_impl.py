from behave import step

from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import create_tosca_epg_ns, instantiate_tosca_epg_ns, \
    eocm_epg_tosca_lcm_workflow_status, eocm_epg_tosca_enm_sync_status
from com_ericsson_do_auto_integration_scripts.EPG_TOSCA_SO_DEPLOYMENT import (upload_vnfd_in_ecm,
                                                                              create_epg_tosca_nsd,
                                                                              upload_epg_tosca_nsd_package,
                                                                              epg_tosca_onboard_day1,
                                                                              onboard_tepg_node_subsytems,
                                                                              onboard_epg_tosca_config_template,
                                                                              onboard_epg_tosca_service_template,
                                                                              create_epg_tosca_network_service,
                                                                              verify_epg_tosca_service_status,
                                                                              check_tepg_lcm_workflow_status,
                                                                              check_tosca_egp_ping_status)
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import (check_epg_ecm_order,
                                                                        check_epg_enm_sync_status)
from com_ericsson_do_auto_integration_scripts.DUMMY_SOL_SO_DEPLOYMENT import verify_dummy_sol_package


@step("I start the Scenario to Upload VNFD in ECM")
def step_impl(context):
    upload_vnfd_in_ecm()


@step("I start the Scenario to Verify onboarded VNFD package")
def step_impl(context):
    verify_dummy_sol_package()


@step("I start the Scenario to Create NSD package")
def step_impl(context):
    create_epg_tosca_nsd()


@step("I start the Scenario to Upload NSD package")
def step_impl(context):
    upload_epg_tosca_nsd_package()


@step("I start the Scenario to Transfer So files to workflow pod")
def step_impl(context):
    epg_tosca_onboard_day1()


@step("I start the Scenario to Onboard the ECM and ENM subsystems to SO")
def step_impl(context):
    onboard_tepg_node_subsytems()


@step("I start the Scenario to Upload additional parameter config files into the SO")
def step_impl(context):
    onboard_epg_tosca_config_template()


@step("I start the Scenario to Onboard service template for node deployment")
def step_impl(context):
    onboard_epg_tosca_service_template()


@step("I start the Scenario to Create the network service using serviceModel ID for Node deployment")
def step_impl(context):
    create_epg_tosca_network_service()


@step("I start the Scenario of polling the state of network service using service ID for deployed node")
def step_impl(context):
    verify_epg_tosca_service_status()


@step("I start the Scenario of checking LCM workflow")
def step_impl(context):
    check_tepg_lcm_workflow_status()


@step("I start the Scenario of checking ECM order status")
def step_impl(context):
    check_epg_ecm_order()


@step("I start the Scenario of checking LCM workflow for tosca EPG")
def step_impl(context):
    eocm_epg_tosca_lcm_workflow_status()


@step("I start the Scenario of checking ECM order status for tosca EPG")
def step_impl(context):
    check_epg_ecm_order()


@step("I start the Scenario of pinging the deployed Node")
def step_impl(context):
    check_tosca_egp_ping_status()


@step("I start the Scenario of checking sync status of node in ENM")
def step_impl(context):
    check_epg_enm_sync_status()


@step("I start the Scenario of checking sync status of epg tosca in ENM")
def step_impl(context):
    eocm_epg_tosca_enm_sync_status()


@step("I start the Scenario to Create NS for TOSCA EPG")
def step_impl(context):
    create_tosca_epg_ns()


@step("I start the Scenario to Instantiate NS for TOSCA EPG")
def step_impl(context):
    instantiate_tosca_epg_ns()
