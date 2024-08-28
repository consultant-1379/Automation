

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
