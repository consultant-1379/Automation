from behave import step
from com_ericsson_do_auto_integration_scripts.CNF_NS_DEPLOYMENT import (create_cnfns_nsd_package,
                                                                        upload_cnfns_nsd_package, create_cnf_ns,
                                                                        instantiate_tosca_cnf_ns)


@step("I start the Scenario to create NSD package")
def step_impl(context):
    create_cnfns_nsd_package()


@step("I start the Scenario to upload NSD package into Cloud Manager")
def step_impl(context):
    upload_cnfns_nsd_package()


@step("I start the Scenario to create NS")
def step_impl(context):
    create_cnf_ns()


@step("I start the Scenario to instantiate NS")
def step_impl(context):
    instantiate_tosca_cnf_ns()
