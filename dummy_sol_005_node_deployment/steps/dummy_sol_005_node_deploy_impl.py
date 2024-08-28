
from behave import *

from com_ericsson_do_auto_integration_scripts.DUMMY_SOL_SO_DEPLOYMENT import *

    
@step("I start the Scenario to Add package download parameter in VNFLCM")
def step_impl(context):
    sol_dummy_package_download_parameter()



@step("I start the Scenario to Create sol dummy node flavor and transfer to VIM")
def step_impl(context):
    create_sol_dummy_flavours()
    
       
@step("I start the Scenario to Upload SOL Dummy VNFD")
def step_impl(context):
    upload_sol_dummy_vnfd()
        
@step("I start the Scenario to Verify onboarded Dummy package")
def step_impl(context):
    verify_dummy_sol_package()
    
    
@step("I start the Scenario to Search SOL Dummy image id and transfer it to VIM")
def step_impl(context):
    search_transfer_sol_dummy_image()
    
    
@step("I start the Scenario to Create SOL Dummy NSD")  
def step_impl(context):
    create_sol_dummy_nsd()


@step("I start the Scenario to Upload SOL Dummy NSD")    
def step_impl(context):
    upload_sol_dummy_nsd_package()



###################################################################################################
# Deployment from SO ...these steps are on SO.

@step("I start the Scenario to onboard ECM SOL005 adapter subsystem to SO")
def step_impl(context):
    onboard_sol_dummy_subsytems()
    
@step("I start the Scenario to onboard the configuration templates for SOL Dummy")
def step_impl(context):
    onboard_sol_dummy_config_template()
        

@step("I start the Scenario to onboard service template")
def step_impl(context):
    onboard_sol_dummy_service_template()
    

@step("I start the Scenario to create the network service using serviceModel ID")
def step_impl(context):
    create_sol_dummy_network_service()


@step("I start the Scenario of polling the state of network service using service ID")
def step_impl(context):
    verify_sol_dummy_service_status()

