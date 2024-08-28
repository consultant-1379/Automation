
from behave import *
from com_ericsson_do_auto_integration_scripts.BGF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.TOSCA_BGF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.IMS_NETWORK_DEPLOYMENT import *


@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_tosca_ssh_key()
    
    


@step("I start the Scenario to Create TOSCA vBGF flavor and transfer to VIM")
def step_impl(context):
    create_tosca_bgf_flavours()
    


    
@step("I start the Scenario to Add package download parameter in VNFLCM")
def step_impl(context):
    tosca_bgf_package_download_parameter()


@step("I start the Scenario to Create security group for TOSCA vBGF")
def step_impl(context):
    create_tosca_bgf_security_group()
    
    

@step("I start the Scenario to Onboard Network Stack for BGF node")
def step_impl(context):
    onboard_bgf_network_template()
    


@step("I start the Scenario to Deploy Network stack for TOSCA BGF Node")
def step_impl(context):
    deploy_bgf_network_template()

##################################################################################################


@step("I start the Scenario to Get zip package name from ECM host blade server")
def step_impl(context):
    get_vnfd_id_tosca_bgf_nodes()


@step("I start the Scenario to Update Onboard file for TOSCA BGF package onboarding")
def step_impl(context):
    update_tosca_bgf_node_onboard_file()



@step("I start the Scenario to Onboard TOSCA BGF package")
def step_impl(context):
    onboard_tosca_bgf_package()


@step("I start the Scenario to Verify onboarded TOSCA BGF package")
def step_impl(context):
    verify_tosca_bgf_package()




@step("I start the Scenario to Search TOSCA vBGF image id and transfer it to VIM")
def step_impl(context):
    search_transfer_tosca_bgf_image()


@step("I start the Scenario to Fetch Network and Subnet Ids to update deploy file")
def step_impl(context):
    fetch_net_subnet_ids_tosca_bgf()


@step("I start the Scenario to Update deploy file for TOSCA BGF Node deployment")
def step_impl(context):
    update_tosca_bgf_node_deploy_file()
    
    
@step("I start the Scenario to Start deploying the TOSCA BGF Node")
def step_impl(context):
    deploy_tosca_bgf_package()
    
    

@step("I start the Scenario to Verify deployed TOSCA BGF Node")
def step_impl(context):
    verify_tosca_bgf_deployment()        

