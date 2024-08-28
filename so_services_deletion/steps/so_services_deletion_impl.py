from behave import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DELETION import *


@step("I start the Scenario to terminate all the services from so")
def step_impl(context):
    start_so_node_deletion()