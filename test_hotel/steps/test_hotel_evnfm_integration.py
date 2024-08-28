from behave import *
from com_ericsson_do_auto_integration_scripts.CNFNS_INSTANTIATION_PRE_REQ import *


@step("I start the Scenario to take a back up of a baseenv file")
def step_impl(context):
    back_up_of_baseenv_file()


@step("I start the Scenario to retrieve HELM repo details from EVNFM")
def step_impl(context):
    retrieve_helm_repo_details('TEST-HOTEL')


@step("I start the Scenario to retrieve Docker registry details from EVNFM")
def step_impl(context):
    retrieve_docker_registry_details('TEST-HOTEL')


@step("I start the Scenario to fetch docker registry certificate")
def step_impl(context):
    retrieve_docker_registry_certificate('TEST-HOTEL')


@step("I start the Scenario to update the baseenv file with the new values")
def step_impl(context):
    update_baseenv_file()


@step("I start the Scenario to configure Docker and HELM registry service")
def step_impl(context):
    configure_helm_and_docker_registry_service()


@step("I start the Scenario to verify the updated values in baseenv file")
def step_impl(context):
    verify_updated_baseenv_file()


@step("I start the Scenario to execute post install script to add NFVO configuration on EVNFM")
def step_impl(context):
    add_nfvo_configuration_evnfm('TEST-HOTEL')


@step("I start the Scenario to register EVNFM for CNF integration")
def step_impl(context):
    register_evnfm_cnf_integration()
