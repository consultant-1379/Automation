from behave import *
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *


@step("I start the Scenario to install workflow")
def step_impl(context):
    install_tosca_pretosca_workflow()

@step("I start the Scenario to modify workflow bundle descriptor")
def step_impl(context):
    modify_workflow_bundle_descriptor()





