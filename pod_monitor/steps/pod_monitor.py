from com_ericsson_do_auto_integration_scripts.POD_MONITOR import check_pod_status
from behave import step


@step("I start the Scenario to Check for unexpected pod restarts")
def step_impl(context):
    check_pod_status()
