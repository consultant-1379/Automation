from behave import step
from com_ericsson_do_auto_integration_scripts.ECM_SERVICE_TERMINATE import terminate_ns_instantiate


@step("I start the Scenario to Terminate the Network Service from ECM")
def step_impl(context):
    terminate_ns_instantiate()
