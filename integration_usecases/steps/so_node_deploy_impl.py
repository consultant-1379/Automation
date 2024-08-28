
from behave import *
from com_ericsson_do_auto_integration_scripts.DUMMY_SO_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
log = Logger.get_logger('so_node_deploy_impl.py')

@step("I start the Scenario to update and transfer the NSD package")
def step_impl(context):
    log.info('Starting script : dummy node deployment from SO')
    Report_file.add_line('Starting script : dummy node deployment from SO')
    update_dummy_nsd_template()


@step('I start the Scenario to Onboard the ECM and ENM subsystems to SO')
def step_impl(context):
    onboard_dummy_subsytems()

@step("I start the Scenario to Deploy NSD package on ECM and Update nsd_id in service template")
def step_impl(context):
    onboard_dummy_nsd_template()


@step("I start the Scenario to onboard service template")
def step_impl(context):
    onboard_dummy_service_template()


@step("I start the Scenario to create the network service using serviceModel ID")
def step_impl(context):
    create_dummy_network_service()


@step("I start the Scenario of polling the state of network service using service ID")
def step_impl(context):
    verify_dummy_service_status()
    log.info('END script : dummy node deployment from SO')
    Report_file.add_line('END script : dummy node deployment from SO')
    
@step("I start the Scenario to verify dummy node deploy workflow version")
def step_impl(context):
    verify_dummy_so_depl_workflow_version()
    
