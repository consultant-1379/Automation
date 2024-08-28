
from behave import *
from com_ericsson_do_auto_integration_scripts.UDS_VFC_OPERATIONS import UDS_VFC as uds_vfc




@step("I start the Scenario to Onboard resource vfc to UDS")
def step_impl(context):
    uds_vfc.onboard_resource_vfc(uds_vfc)
    

@step("I start the Scenario to certify resource vfc to UDS")
def step_impl(context):    
    uds_vfc.certify_resource_vfc(uds_vfc)


@step("I start the Scenario to Onboard network function vfc to UDS")
def step_impl(context):    
    uds_vfc.onboard_network_function_vfc(uds_vfc)
    

@step("I start the Scenario to certify network function vfc to UDS")
def step_impl(context):    
    uds_vfc.certify_network_function_vfc(uds_vfc)
    


@step("I start the Scenario to Onboard network service vfc to UDS")
def step_impl(context):    
    uds_vfc.onboard_network_service_vfc(uds_vfc)
    

@step("I start the Scenario to certify network service vfc to UDS")
def step_impl(context):    
    uds_vfc.certify_network_service_vfc(uds_vfc)
    

    
@step("I start the Scenario to Onboard epg vfc to UDS")
def step_impl(context):    
    uds_vfc.onboard_epg_vfc(uds_vfc)
    
	
@step("I start the Scenario to certify epg vfc to UDS")
def step_impl(context):    
    uds_vfc.certify_epg_vfc(uds_vfc)
    
