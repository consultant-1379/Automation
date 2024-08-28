from behave import step
from com_ericsson_do_auto_integration_scripts.CNF_NS_DEPLOYMENT import remove_cnf_ns

@step("I start the Scenario to remove cnf vapp from ns")
def step_impl(context):
    remove_cnf_ns()
