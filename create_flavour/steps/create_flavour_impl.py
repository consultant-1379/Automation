from behave import *

from com_ericsson_do_auto_integration_scripts.ECM_RANDOM_OPERATIONS import *


@step("I start the Scenario to create the flavour")
def step_impl(context):
    start_flavour_creation()

