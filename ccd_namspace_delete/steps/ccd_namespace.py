from behave import *
from com_ericsson_do_auto_integration_scripts.EVNFM_NODE_TERMINATE import CCD_namespace_delete


@step("I start the Scenario to Delete namespaces given in jenkins job")
def step_impl(context):
    CCD_namespace_delete()
