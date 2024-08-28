from behave import *
from com_ericsson_do_auto_integration_scripts.ECDE_SPINNAKER_CLEANUP import *


@step("I start the Scenario to Extract token for admin")
def step_impl(context):
    extract_token_for_admin()


@step("I start the Scenario to fetch and delete the pipeline")
def step_impl(context):
    extract_access_token_for_spinnaker()


