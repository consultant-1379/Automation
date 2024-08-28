from behave import *
from com_ericsson_do_auto_integration_scripts.NODESELCTOR_VERIFICATION import *


@then("I start the Scenario to Check that the EO deployment pods are deployed with the nodeSelector key")
def step_impl(context):
    nodeselector_check()
