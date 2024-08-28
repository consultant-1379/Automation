from behave import *
from com_ericsson_do_auto_integration_scripts.OPENSTACK_STACK_CLEANUP import delete_stacks_from_openstack


@step("I Start the Scenario to delete stacks from OPENSTACK")
def step_impl(context):
    delete_stacks_from_openstack()
