
from behave import *
from com_ericsson_do_auto_integration_scripts.MME_SO_DEPLOYMENT import *


@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):
    remove_LCM_entry_mme()
    
    


@step("I start the Scenario to Add admin and heat_stack_owner roles to project user")
def step_impl(context):
    admin_heatstack_rights_mme()
    
    
    
    
    

@step("I start the Scenario to Update VNFLCM OSS Password")
def step_impl(context):
    update_lcm_password_mme()
    



@step("I start the Scenario to Copy the MME software from HOST blade to VNF-LCM")
def step_impl(context):
    transfer_mme_software()
    
    
    


@step("I start the Scenario to Extract MME software on VNF-LCM Server")
def step_impl(context):
    #this method calling is removed from feature file , as there is no tar now.
    unpack_mme_software()
    



@step("I start the Scenario to Install the vMME workflow on VNF-LCM")
def step_impl(context):
    mme_workflow_deployment()
    

@step("I start the Scenario to Install the vMME workflow on VM-VNFM")
def step_impl(context):
    mme_workflow_deployment_vm_vnfm()


@step("I start the Scenario to Update db table with MME entries for instantiate and terminate")
def step_impl(context):
    update_db_table()


@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_ssh_key_mme()
    



@step("I start the Scenario to Create Flavors for MME deployment")
def step_impl(context):
    create_mme_flavors()
    



@step("I start the Scenario to Register Images for MME deployment")
def step_impl(context):
    create_mme_images()


@step("I start the Scenario to Transfer So files to workflow pod")
def step_impl(context):
    mme_so_files_transfer()


@step("I start the Scenario to upload IPAM for MME deployment")
def step_impl(context):
    upload_ipam()


@step("I start the Scenario to Start onboarding the IPAM package")    
def step_impl(context):    
    onboard_ipam_package() 


@step("I start the Scenario to Update Onboard file for MME package onboarding")
def step_impl(context):
    update_mme_onboard_file()
    


@step("I start the Scenario to Start onboarding the MME package")
def step_impl(context):
    onboard_mme_package()
    


@step("I start the Scenario to Verify onboarded MME package")
def step_impl(context):
    verify_mme_package()
    



@step("I start the Scenario to Fetch NSD package from ECM to prepare ns1.yaml file")
def step_impl(context):
    fetch_mme_nsd_package()


@step("I start the Scenario to Update NSD package and CSAR it")
def step_impl(context):
    update_mme_nsd_template()


@step("I start the Scenario to Onboard the ECM and ENM subsystems to SO")
def step_impl(context):
    onboard_mme_subsytems()


@step("I start the Scenario to Start onboarding the NSD package")
def step_impl(context):
    onboard_mme_nsd_template()


@step("I start the Scenario to onboard service template for node deployment")
def step_impl(context):
    onboard_mme_service_template()


@step("I start the Scenario to create the network service using serviceModel ID for Node deployment")
def step_impl(context):
    create_mme_network_service()



@step("I start the Scenario of checking in SO for workflow deployment status")
def step_impl(context):
    check_mme_so_deploy_attribute()


@step("I start the Scenario of checking in SO for Node sync in ENM status")
def step_impl(context):
    check_mme_so_day1_configure_status()


@step("I start the Scenario of polling the state of network service using service ID for deployed node")
def step_impl(context):
    verify_mme_service_status()


@step("I start the Scenario of pinging the deployed Node")
def step_impl(context):
    check_mme_ip_ping_status()


@step("I start the Scenario of checking bulk configuration")
def step_impl(context):
    check_mme_bulk_configuration()


@step("I start the Scenario of checking LCM workflow")
def step_impl(context):
    check_mme_lcm_workflow_status()



@step("I start the Scenario of checking ECM order status")
def step_impl(context):
    check_mme_ecm_order()


@step("I start the Scenario of checking sync status of node in ENM")
def step_impl(context):
    check_mme_enm_sync_status()


@step("I start the Scenario to Update deploy file for MME Node deployment")
def step_impl(context):
    update_deploy_file_mme_ecm()


@step("I start the Scenario to Start deploying the MME Node")
def step_impl(context):
    deploy_mme_package_ecm()


@step("I start the Scenario to Verify deployed MME Node")
def step_impl(context):
    verify_mme_deployment_ecm()