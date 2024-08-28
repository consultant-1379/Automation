from behave import step
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
                                                                              fetch_and_update_subnet_data)
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import check_epg_ecm_order, \
    create_uds_so_tepg_network_service
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


@step("I start the Scenario to Onboard the ECM and ENM subsystems to SO")
def step_impl(context):
    onboard_tepg_node_subsytems()


@step("I start the Scenario to Create Network Service for EPG deployment using UDS service template")
def step_impl(context):
    fetch_and_update_subnet_data()
    create_uds_so_tepg_network_service()


@step("I start the Scenario of Polling the state of network service using service ID")
def step_impl(context):
    verify_epg_tosca_service_status()


@step("I start the Scenario of checking LCM workflow")
def step_impl(context):
    check_tepg_lcm_workflow_status()


@step("I start the Scenario of checking ECM order status")
def step_impl(context):
    check_epg_ecm_order()
