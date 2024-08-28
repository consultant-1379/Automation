from behave import *
from com_ericsson_do_auto_integration_scripts.ECDE_TEST_ENV_SETUP import *


@step("I start the Scenario to Create AAT tool in ECDE Test tools")
def step_impl(context):
    create_ecde_aat_tool()



@step("I start the Scenario to Create a testcase under Test tool")
def step_impl(context):
    add_testcase_to_aat_tool()
   


@step("I start the Scenario to Create a testsuite with testcase added to Test tool")
def step_impl(context):
    add_ecde_testsuit()


@step("I start the Scenario to Clean all the TEP from spinnaker")
def step_impl(context):
    clean_ecde_spinnaker()



