from behave import step
from com_ericsson_do_auto_integration_scripts.UDS_SERVICE_TEMPLATE_CREATION import *

@step("I start the Scenario to Create Service in UDS")
def step_impl(context):
    create_uds_service()

@step("I start the Scenario to Fetch and update VFC data")
def step_impl(context):
    fetch_and_update_vfc_data()

@step("I start the Scenario to Checkout vfc virtNetworkServ")
def step_impl(context):
    checkout_vfc("NS")

@step("I start the Scenario to Add properties to VfC")
def step_impl(context):
    add_properties_to_vfc("NS")

@step("I start the Scenario to certify VfC")
def step_impl(context):
    certify_vfc("NS")

@step("I start the Scenario to Add VFC to Service")
def step_impl(context):
    for VFC in ["GEOSITE", "VIMZONE0", "SUBSYSTEM", "NS", "EPG"]:
        add_vfc_to_the_service(VFC)

@step("I start the Scenario to declare inputs to VFC")
def step_impl(context):
    for VFC in ["GEOSITE", "VIMZONE0", "SUBSYSTEM", "NS", "EPG"]:
        declare_vfc_inputs(VFC)

@step("I start the Scenario to Add values to VFC inputs")
def step_impl(context):
    for VFC in ["GEOSITE", "VIMZONE0", "SUBSYSTEM", "NS", "EPG"]:
        add_values_to_the_vfc_inputs(VFC)

@step("I start the Scenario to Add values to VFC properties")
def step_impl(context):
    for VFC in ["GEOSITE", "VIMZONE0", "SUBSYSTEM", "NS", "EPG"]:
        add_values_to_vfc_properties(VFC)

@step("I start the Scenario to Add inputs to NETWORK_SERVICE")
def step_impl(context):
    add_inputs_to_vfc("NS")

@step("I start the Scenario to Add tosca function to NETWORK_SERVICE")
def step_impl(context):
    add_vfc_tosca_function("NS")

@step("I start the Scenario to Add directives to VFC")
def step_impl(context):
    for VFC in ["GEOSITE", "VIMZONE0", "SUBSYSTEM"]:
        add_vfc_directives(VFC)

@step("I start the Scenario to Add node filter properties")
def step_impl(context):
    for VFC in ["GEOSITE", "VIMZONE0", "SUBSYSTEM"]:
        add_vfc_node_filter_properties(VFC)

@step("I start the Scenario to associate two vfcs")
def step_impl(context):
    associate_two_vfcs("VIMZONE0", "GEOSITE")
    associate_two_vfcs("EPG", "VIMZONE0")
    associate_two_vfcs("EPG", "NS")
    associate_two_vfcs("NS", "SUBSYSTEM")

@step("I start the Scenario to Upload config template")
def step_impl(context):
    upload_tosca_epg_config_templates()
    upload_tosca_epg_day1config_templates()

@step("I start the Scenario to Certify service")
def step_impl(context):
    certify_service()

@step("I start the Scenario to Distribute service to SO")
def step_impl(context):
    distribute_the_service_to_so()






