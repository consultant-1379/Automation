
from behave import *
from com_ericsson_do_auto_integration_scripts.UDS_VF_OPERATIONS import UDS_VF as uds_vf


@step("I start the Scenario to Create vf to UDS")
def step_impl(context):
    uds_vf.create_vf(uds_vf)
    

@step("I start the Scenario to Add EPG vfc to vf composition")
def step_impl(context):    
    uds_vf.add_epg_vfc_to_vf_composition(uds_vf)


@step("I start the Scenario to Add network_service vfc to vf composition")
def step_impl(context):    
    uds_vf.add_network_service_vfc_to_vf_composition(uds_vf)
    

@step("I start the Scenario to Associate epg to network service")
def step_impl(context):    
    uds_vf.associate_epg_to_network_service(uds_vf)
    


@step("I start the Scenario to Onboard the ECM request template")
def step_impl(context):    
    uds_vf.onboard_the_ecmrequest_template(uds_vf)
    

@step("I start the Scenario to Onboard the day1config template")
def step_impl(context):    
    uds_vf.onboard_the_day1config_template(uds_vf)
    

    
@step("I start the Scenario to Create EPG inputs")
def step_impl(context):    
    uds_vf.create_epg_inputs(uds_vf)
    

@step("I start the Scenario to Create Network Service inputs")
def step_impl(context):    
    uds_vf.create_ns_inputs(uds_vf)
    

@step("I start the Scenario to Add EPG properties")
def step_impl(context):    
    uds_vf.add_epg_properties(uds_vf)



@step("I start the Scenario to Add Network Service properties")
def step_impl(context):    
    uds_vf.add_ns_properties(uds_vf)


@step("I start the Scenario to Certify created VF")
def step_impl(context):    
    uds_vf.certify_created_vf(uds_vf)
