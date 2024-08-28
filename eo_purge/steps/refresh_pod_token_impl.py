from behave import  *
from com_ericsson_do_auto_integration_scripts.EO_PURGE import *
from com_ericsson_do_auto_integration_scripts.REFRESH_POD_TOKEN import refresh_pod_token_eo


@step("I start the Scenario to refresh cinder pod token")
def step_impl(context):
    refresh_pod_token_eo()
