from behave import *
from com_ericsson_do_auto_integration_scripts.BGF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.IMS_NETWORK_DEPLOYMENT import *


@step("I start the Scenario to Remove old LCM entry from known_hosts file on Host server")
def step_impl(context):
    remove_LCM_entry()


@step("I start the Scenario to Add admin and heat_stack_owner roles to project user")
def step_impl(context):
    admin_heatstack_rights()


@step("I start the Scenario to Update VNFLCM OSS Password")
def step_impl(context):
    update_lcm_password()


@step("I start the Scenario to Copy the BGF software from HOST blade to VNF-LCM")
def step_impl(context):
    transfer_bgf_software()


@step("I start the Scenario to Extract BGF software on VNF-LCM Server")
def step_impl(context):
    unpack_bgf_software()


@step("I start the Scenario to Install the vBGF workflow on VNF-LCM")
def step_impl(context):
    bgf_workflow_deployment()


@step("I start the Scenario to Generate ssh keys using JBOSS user")
def step_impl(context):
    generate_ssh_key()


@step("I start the Scenario to Create Flavors for BGF deployment")
def step_impl(context):
    create_bgf_flavours()


@step("I start the Scenario to Register Images for BGF deployment")
def step_impl(context):
    register_bgf_images()


@step("I start the Scenario to Onboard Network Stack for BGF node")
def step_impl(context):
    onboard_bgf_network_template()


@step("I start the Scenario to Deploy Network Stack for BGF node")
def step_impl(context):
    deploy_bgf_network_template()


@step("I start the Scenario to Transfer So files to workflow pod")
def step_impl(context):
    # sbg_so_files_transfer()
    pass


@step("I start the Scenario to Update Onboard file for BGF package onboarding")
def step_impl(context):
    update_bgf_node_onboard_file()


@step("I start the Scenario to Start onboarding the BGF package")
def step_impl(context):
    onboard_bgf_package()


@step("I start the Scenario to Verify onboarded BGF package")
def step_impl(context):
    verify_bgf_package()


@step("I start the Scenario to Update deploy file for BGF Node deployment")
def step_impl(context):
    update_bgf_node_deploy_file()


@step("I start the Scenario to Start deploying the BGF Node")
def step_impl(context):
    deploy_bgf_package()


@step("I start the Scenario to Verify deployed BGF Node")
def step_impl(context):
    verify_bgf_deployment()


@step("I start the Scenario to Get VNFD ID from ECM host blade server")
def step_impl(context):
    get_vnfd_id_bgf_nodes()
