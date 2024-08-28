from behave import step
from com_ericsson_do_auto_integration_scripts.CNF_NS_DEPLOYMENT import add_cnf_ns


@step("I start the Scenario to add cnf vapp in ns")
def step_impl(context):
    add_cnf_ns()
