from behave import *
from com_ericsson_do_auto_integration_scripts.SO_Cleanup import *

@step("I start the Scenario to delete services and subsystems")
def step_impl(context):
    start_so_cleanup()
    