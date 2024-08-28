
from behave import *
from com_ericsson_do_auto_integration_scripts.ETSI_TOSCA_DUMMY_DEPLOYMENT import *


@step("I start the Scenario to Remove old vnflaf package from vnflcm")
def step_impl(context):
    remove_old_vnflaf_dir()

@step("I start the Scenario to Create Flavors for ETSI Dummy Tosca deployment")
def step_impl(context):
    create_etsi_tosca_dummy_depl_flavours()
    
@step("I start the Scenario to add ETSI Dummy Tosca Package download parameter")
def step_impl(context):
    etsi_tosca_package_download_parameter()


@step("I start the Scenario to Get zip package name from ECM host blade server for dummy Tosca")
def step_impl(context):
    get_vnfd_id_tosca_dummy_nodes()
        
@step("I start the Scenario to Update Onboard file for ETSI Dummy Tosca Deployment package onboarding")
def step_impl(context):
    update_tosca_dummy_node_onboard_file()
    

@step("I start the Scenario to Start onboarding the Dummy Tosca deployment package")
def step_impl(context):
    create_etis_dummy_package_in_cm()


@step("I start the Scenario to Verify onboarded ETSI Dummy Tosca package")
def step_impl(context):
    verify_etis_dummy_package_in_cm()

    
@step("I start the Scenario to transfer ETSI Dummy Tosca image to openstack")
def step_impl(context):
    transfer_dummy_image_openstack()

@step("I start the Scenario to Update deploy Dummy Tosca ETSI file")
def step_impl(context):
    update_tosca_dummy_node_deploy_file()
    
    

@step("I start the Scenario to Start deploying the ETSI Dummy Tosca Node")
def step_impl(context):
    deploy_dummy_tosca_package()
    
@step("I start the Scenario to Verify ETSI Dummy Tosca deployment Node")
def step_impl(context):
    verify_etsi_dummy_deployment()
    
@step("I start the Scenario to Verify ETSI Dummy Tosca Workflow verison")
def step_impl(context):
    verfiy_etsi_dummy_tosca_workflow_version()

    


