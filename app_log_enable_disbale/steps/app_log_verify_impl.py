from behave import step
from com_ericsson_do_auto_integration_scripts.AppLogEnable import AppLogEnable


@step("I start the Scenario to Enable the debug logs for given applications")
def step_impl(context):
    AppLogEnable.start_enable_debug_logs(AppLogEnable)


@step("I start the Scenario to Disable the debug logs for given applications")
def step_impl(context):
    AppLogEnable.start_disable_debug_logs(AppLogEnable)
