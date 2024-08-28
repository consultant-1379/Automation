
from behave import *
from com_ericsson_do_auto_integration_scripts.SBG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.IMS_NETWORK_DEPLOYMENT import *



@step("I start the Scenario to Get VNFD ID from ECM host blade server")
def step_impl(context):    
    get_vnfd_id_sbg_nodes()    

@step("I start the Scenario to Copy the SBG software from HOST blade to VNF-LCM")
def step_impl(context):
    transfer_sbg_software()
    

@step("I start the Scenario to Extract SBG software on VNF-LCM Server")
def step_impl(context):
    unpack_sbg_software()
    
    
@step("I start the Scenario to Install the vSBG workflow on VNF-LCM")
def step_impl(context):
    sbg_workflow_deployment()


@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_ssh_key()
    
    

@step("I start the Scenario to Create Flavors for SBG deployment")
def step_impl(context):
    create_sbg_flavours()
    



@step("I start the Scenario to Register Images for SBG deployment")
def step_impl(context):
    register_sbg_images()
    
 
@step("I start the Scenario to Onboard Network Stack for SBG node")
def step_impl(context):
    onboard_sbg_network_template()
    
    
@step("I start the Scenario to Deploy Network Stack for SBG node")
def step_impl(context):
    deploy_sbg_network_template()   
    

@step("I start the Scenario to Transfer So files to workflow pod")
def step_impl(context):
    #sbg_so_files_transfer()
    pass
    
    


@step("I start the Scenario to Update Onboard file for SBG package onboarding")
def step_impl(context):
    update_sbg_node_onboard_file()
    


@step("I start the Scenario to Start onboarding the SBG package")
def step_impl(context):
    onboard_sbg_package()
    


@step("I start the Scenario to Verify onboarded SBG package")
def step_impl(context):
    verify_sbg_package()
    


@step("I start the Scenario to Update deploy file for SBG Node deployment")
def step_impl(context):
    update_sbg_node_deploy_file()
    


@step("I start the Scenario to Start deploying the SBG Node")
def step_impl(context):
    deploy_sbg_package()
    


@step("I start the Scenario to Verify deployed SBG Node")
def step_impl(context):
    verify_sbg_deployment()

