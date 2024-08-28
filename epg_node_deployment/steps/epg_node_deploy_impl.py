
from behave import *
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *


@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):
    remove_LCM_entry()
    
    
    
    


@step("I start the Scenario to Add admin and heat_stack_owner roles to project user")
def step_impl(context):
    admin_heatstack_rights()

    

@step("I start the Scenario to Update VNFLCM OSS Password")
def step_impl(context):
    update_lcm_password()
    


@step("I start the Scenario to Copy the EPG software from HOST blade to VNF-LCM")
def step_impl(context):
    transfer_epg_software()
    
    


@step("I start the Scenario to Extract EPG software on VNF-LCM Server")
def step_impl(context):
    #this method calling is removed from feature file , as there is no tar now.
    unpack_epg_software()
    



@step("I start the Scenario to Install the vEPG workflow on VNF-LCM")
def step_impl(context):
    workflow_deployment()



@step("I start the Scenario to Install the vEPG workflow on VM-VNFM")
def step_impl(context):
    workflow_deployment()
    


@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_ssh_key()
    
    
    
    
    


@step("I start the Scenario to Create Flavors for EPG deployment")
def step_impl(context):
    create_epg_flavours()
    



@step("I start the Scenario to Register Images for EPG deployment")
def step_impl(context):
    register_epg_images()
    




@step("I start the Scenario to Update Onboard file for EPG package onboarding")
def step_impl(context):
    update_onboard_file()
    


@step("I start the Scenario to Start onboarding the EPG package")
def step_impl(context):
    onboard_epg_package()
    


@step("I start the Scenario to Verify onboarded EPG package")
def step_impl(context):
    verify_epg_package()
    

@step("I start the Scenario to Transfer So files to workflow pod")
def step_impl(context):
    epg_so_files_transfer()
    


@step("I start the Scenario to Update deploy file for EPG Node deployment")
def step_impl(context):
    update_deploy_file_epg_ecm()
    


@step("I start the Scenario to Start deploying the EPG Node")
def step_impl(context):
    deploy_epg_package()
    


@step("I start the Scenario to Verify deployed EPG Node")
def step_impl(context):
    verify_epg_deployment()

