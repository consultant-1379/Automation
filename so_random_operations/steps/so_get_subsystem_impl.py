from behave import *
from com_ericsson_do_auto_integration_scripts.SO_RANDOM_OPERATIONS import *


@step('I start the Scenario to Get SO Subsystem in an infinite loop')
def step_impl(context):
    get_subsystem_loop()
