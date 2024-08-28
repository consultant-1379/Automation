
from behave import *
from com_ericsson_do_auto_integration_scripts.CSCF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.IMS_NETWORK_DEPLOYMENT import *

@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):
    #remove_LCM_entry()
    pass

    
    
    
@step("I start the Scenario to Add admin and heat_stack_owner roles to project user")
def step_impl(context):
    #admin_heatstack_rights()
    pass
       
    
    

@step("I start the Scenario to Update VNFLCM OSS Password")
def step_impl(context):
    #update_lcm_password()
    pass
    
    

@step("I start the Scenario to Copy the CSCF software from HOST blade to VNF-LCM")
def step_impl(context):
    transfer_cscf_software()


@step("I start the Scenario to Extract CSCF software on VNF-LCM Server")
def step_impl(context):
    unpack_cscf_software()
    


@step("I start the Scenario to Install the vCSCF workflow on VNF-LCM")
def step_impl(context):
    cscf_workflow_deployment()
    


@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_ssh_key()  


@step("I start the Scenario to Create Flavors for CSCF deployment")
def step_impl(context):
    create_cscf_flavours()
    

@step("I start the Scenario to Register Images for CSCF deployment")
def step_impl(context):
    register_cscf_images()
    

@step("I start the Scenario to Onboard Network Stack for CSCF node")
def step_impl(context):
    onboard_cscf_network_template()
    

@step("I start the Scenario to Deploy Network Stack for CSCF node")
def step_impl(context):
    deploy_cscf_network_template()


@step("I start the Scenario to Transfer So files to workflow pod")
def step_impl(context):
    #cscf_so_files_transfer()
    pass
      


@step("I start the Scenario to Update Onboard file for CSCF package onboarding")
def step_impl(context):
    update_cscf_node_onboard_file()
    


@step("I start the Scenario to Start onboarding the CSCF package")
def step_impl(context):
    onboard_cscf_package()
    


@step("I start the Scenario to Verify onboarded CSCF package")
def step_impl(context):
    verify_cscf_package()
    


@step("I start the Scenario to Update deploy file for CSCF Node deployment")
def step_impl(context):
    update_cscf_node_deploy_file()
    


@step("I start the Scenario to Start deploying the CSCF Node")
def step_impl(context):
    deploy_cscf_package()
    


@step("I start the Scenario to Verify deployed CSCF Node")
def step_impl(context):
    verify_cscf_deployment()



@step("I start the Scenario to Get VNFD ID from ECM host blade server")
def step_impl(context):    
    get_vnfd_id_cscf_nodes()

