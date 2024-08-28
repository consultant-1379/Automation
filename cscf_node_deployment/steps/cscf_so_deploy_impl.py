from behave import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *


@step("I start the Scenario to Fetch NSD package from ECM to prepare ns1.yaml file")
def step_impl(context):
    fetch_node_nsd_package()


@step("I start the Scenario to Update NSD package and CSAR it")
def step_impl(context):
    update_node_nsd_template()


@step("I start the Scenario to Start onboarding the NSD package")
def step_impl(context):
    onboard_node_nsd_template()


@step("I start the Scenario to Onboard the ECM and ENM subsystems to SO")
def step_impl(context):
    onboard_node_subsytems()


@step("I start the Scenario to onboard service template for node deployment")
def step_impl(context):
    onboard_node_service_template()


@step("I start the Scenario to create the network service using serviceModel ID for Node deployment")
def step_impl(context):
    create_node_network_service()



@step("I start the Scenario of polling the state of network service using service ID for deployed node")
def step_impl(context):
    verify_node_service_status()


