
from behave import *
from com_ericsson_do_auto_integration_scripts.EPG_TOSCA_PREREQUISITE import *


@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):
    remove_lcm_entry_epg_tosca()
    
    
@step("I start the Scenario to Add admin and heat_stack_owner roles to project user")
def step_impl(context):
    admin_heatstack_rights_epg_tosca()


@step("I start the Scenario to Update VNFLCM OSS Password")
def step_impl(context):
    update_lcm_password_epg_tosca()
    

@step("I start the Scenario to Copy EPG workflow software from HOST blade to VNF-LCM")
def step_impl(context):
    transfer_workflow_software()
    

@step("I start the Scenario to Install the vEPG workflow on VNF-LCM")
def step_impl(context):
    epg_tosca_workflow_deployment()


@step("I start the Scenario to Create Flavors for EPG TOSCA deployment")
def step_impl(context):
    create_epg_flavours()


@step("I start the Scenario to Register Images for EPG TOSCA deployment")
def step_impl(context):
    register_epg_images()


@step("I start the Scenario to Prepare VNFD package")
def step_impl(context):
    prepare_vnfd_package()
