
from behave import *
from com_ericsson_do_auto_integration_scripts.UDS_SERVICE_OPERATIONS import UDS_SERVICE as uds_service
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *

@step("I start the Scenario to Create Service in UDS")
def step_impl(context):
    uds_service.create_uds_service(uds_service)
    

@step("I start the Scenario to Add VF to Service")
def step_impl(context):    
    uds_service.add_vf_to_the_service(uds_service)


@step("I start the Scenario to Certify the Service")
def step_impl(context):    
    uds_service.certify_the_service(uds_service)
    

@step("I start the Scenario to Distribute the Service to SO")
def step_impl(context):    
    uds_service.distribute_the_service(uds_service)


@step("I start the Scenario to Verify Service template onboarded to SO")
def step_impl(context):    
    fetch_service_modelId_uds_so_template("EPG")
