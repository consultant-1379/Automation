from behave import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *


@step("I start the Scenario to fetch ccd version")
def step_impl(context):
    fetch_ccd_version()
