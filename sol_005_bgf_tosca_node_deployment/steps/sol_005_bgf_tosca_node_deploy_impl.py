
from behave import *
from com_ericsson_do_auto_integration_scripts.BGF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.TOSCA_BGF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SOL_BGF_SO_DEPLOYMENT import *



@step("I start the Scenario to Onboard vBGF TOSCA Hot Package")
def step_impl(context):
    onboard_sol_tosca_bgf_package()
    


@step("I start the Scenario to Deploy vBGF TOSCA Hot Package")
def step_impl(context):
    deploy_sol_tosca_bgf_package()
    

@step("I start the Scenario to Create TOSCA vBGF flavor and transfer to VIM")
def step_impl(context):
    create_tosca_sol_bgf_flavours()



@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):    
    remove_host_lcm_entry()
    

@step("I start the Scenario to Install the workflow on VNF-LCM")
def step_impl(context):
    
    sol005_bgf_workflow_deployment()
    
        
@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_sol005_tosca_ssh_key()
    
    
@step("I start the Scenario to Add package download parameter in VNFLCM")
def step_impl(context):
    tosca_bgf_package_download_parameter()



##################################################################################################
# Deployment from SO only but these steps are on ECM.

@step("I start the Scenario to copy SSH key on LCM")
def step_impl(context):
    transfer_ssh_key_jboss()
    
    
@step("I start the Scenario to Upload TOSCA SOL BGF VNFD")
def step_impl(context):
    upload_sol_tosca_vnfd()
        
@step("I start the Scenario to Verify onboarded TOSCA BGF package")
def step_impl(context):
    verify_tosca_bgf_package()
    
    
@step("I start the Scenario to Search TOSCA SOL vBGF image id and transfer it to VIM")
def step_impl(context):
    search_transfer_sol_tosca_bgf_image()
    
    
@step("I start the Scenario to Create TOSCA SOL BGF NSD")  
def step_impl(context):
    create_sol_tosca_nsd()


@step("I start the Scenario to Upload TOSCA SOL BGF NSD")    
def step_impl(context):
    upload_sol_tosca_nsd_package()


###################################################################################################
# Deployment from SO ...these steps are on SO.

@step("I start the Scenario to onboard ECM SOL005 adapter subsystem to SO")
def step_impl(context):
    onboard_sol_bgf_subsytems()
    
@step("I start the Scenario to onboard the configuration templates for SOL BGF")
def step_impl(context):
    onboard_sol_bgf_config_template()
        

@step("I start the Scenario to onboard service template")
def step_impl(context):
    onboard_sol_bgf_service_template()
    

@step("I start the Scenario to create the network service using serviceModel ID")
def step_impl(context):
    create_sol_bgf_network_service()


@step("I start the Scenario of polling the state of network service using service ID")
def step_impl(context):
    verify_sol_bgf_service_status()
