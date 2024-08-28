from behave import *
from com_ericsson_do_auto_integration_scripts.GENERIC_WORKFLOW_INSTALL import *


@step("I start the Scenario to install generic workflow")
def step_impl(context):
    start_generic_workflow_install()
