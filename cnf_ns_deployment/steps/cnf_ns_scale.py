from behave import step
from com_ericsson_do_auto_integration_scripts.CNF_NS_DEPLOYMENT import scale_in_ns_cnf_vapp, scale_out_ns_cnf_vapp


@step("I start the Scenario to Scale out cnf vapp in NS")
def step_impl(context):
    scale_out_ns_cnf_vapp()


@step("I start the Scenario to Scale in cnf vapp in NS")
def step_impl(context):
    scale_in_ns_cnf_vapp()
