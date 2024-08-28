from behave import *
from com_ericsson_do_auto_integration_scripts.COLLECT_RUNTIME_DATA import *


@step("I start the Scenario to Collect and update in the runtime file if any new attribute exists in local runtime file")
def step_impl(context):
    collect_run_time_data()





