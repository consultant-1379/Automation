from behave import step
from com_ericsson_do_auto_integration_scripts.PROJ_VIM import (add_test_hotel_external_network)


@step("I start the Scenario to create the External Network")
def step_impl(context):
    add_test_hotel_external_network()

