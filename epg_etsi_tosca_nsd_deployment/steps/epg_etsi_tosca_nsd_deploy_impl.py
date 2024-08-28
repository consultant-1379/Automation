
from behave import *
from com_ericsson_do_auto_integration_scripts.EPG_ETSI_TOSCA_NSD_PREREQUISITE import *

@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):
    remove_LCM_entry_epg_etsi()
    
    
@step("I start the Scenario to Add admin and heat_stack_owner roles to project user")
def step_impl(context):
    admin_heatstack_rights_epg_etsi()

    

@step("I start the Scenario to Update VNFLCM OSS Password")
def step_impl(context):
    update_lcm_password_epg_etsi()
    


@step("I start the Scenario to Copy the EPG ETSI TOSCA NSD software from HOST blade to VNF-LCM")
def step_impl(context):
    transfer_epg_etsi_tosca_nsd_software()
    
    


@step("I start the Scenario to Extract EPG ETSI TOSCA NSD software on VNF-LCM Server")
def step_impl(context):
    #this method calling is removed from feature file , as there is no tar now.
    unpack_epg_etsi_software()
    



@step("I start the Scenario to Install the vEPG workflow on VNF-LCM")
def step_impl(context):
    epg_etsi_nsd_workflow_deployment()



@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_ssh_key_epg_etsi()
    
    
@step("I start the Scenario to Create Flavors for EPG ETSI TOSCA NSD deployment")
def step_impl(context):
    create_epg_etsi_flavours()



@step("I start the Scenario to Register Images for EPG ETSI TOSCA NSD deployment")
def step_impl(context):
    register_epg_etsi_images()
    


