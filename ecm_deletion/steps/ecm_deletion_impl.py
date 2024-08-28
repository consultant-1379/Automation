from behave import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DELETION import *


@step("I start the Scenario to terminate all the nodes and network from ecm")
def step_impl(context):
    start_ecm_node_deletion()