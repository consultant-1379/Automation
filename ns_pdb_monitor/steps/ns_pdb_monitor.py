from com_ericsson_do_auto_integration_scripts.NS_PDB_MONITOR import check_ns_pdb_value
from behave import step


@step("I start the Scenario to Check the pdb value for given namespace")
def step_impl(context):
    check_ns_pdb_value()
