

from behave import *
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import *

@step("I start the Scenario to Scale out")
def step_impl(context):
    start_scale_out()


@step("I start the Scenario to Scale in")
def step_impl(context):
    start_scale_in()


@step("I start the Scenario to Heal")
def step_impl(context):
    start_heal()

@step("I start the Scenario to verify DUMMY Node Heal workflow version")
def step_impl(context):
    verify_node_heal_workflow_version()
    
@step("I start the Scenario verify workflow version of SO Dummy VM Shutdown Scale Heal")
def step_impl(context):
    verify_node_heal_workflow_version()


