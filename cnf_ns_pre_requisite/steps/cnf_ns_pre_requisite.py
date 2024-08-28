from behave import step
from com_ericsson_do_auto_integration_scripts.CNFNS_INSTANTIATION_PRE_REQ import back_up_of_baseenv_file, \
    retrieve_helm_repo_details, retrieve_docker_registry_details, retrieve_helm_repo_details_cn, \
    retrieve_docker_registry_details_cn, retrieve_docker_registry_certificate, \
    retrieve_docker_registry_certificate_cn, retrieve_helm_registry_certificate, update_baseenv_file, \
    configure_helm_and_docker_registry_service, verify_updated_baseenv_file, add_nfvo_configuration_evnfm, \
    register_evnfm_cnf_integration, restart_pods_eocm
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core

@step("I start the Scenario to take a back up of a baseenv file")
def step_impl(context):
    back_up_of_baseenv_file()

@step("I start the Scenario to retrieve HELM repo details from EVNFM")
def step_impl(context):
    Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        retrieve_helm_repo_details_cn()
    else:
        retrieve_helm_repo_details()

@step("I start the Scenario to retrieve Docker registry details from EVNFM")
def step_impl(context):
    Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        retrieve_docker_registry_details_cn()
    else:
        retrieve_docker_registry_details()

@step("I start the Scenario to fetch docker registry certificate")
def step_impl(context):
    Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        retrieve_docker_registry_certificate_cn()
    else:
        retrieve_docker_registry_certificate()

@step("I start the Scenario to fetch helm certificate")
def step_imp(context):
    retrieve_helm_registry_certificate()

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
    add_nfvo_configuration_evnfm()

@step("I start the Scenario to register EVNFM for CNF integration")
def step_impl(context):
    register_evnfm_cnf_integration()

@step("I start the scenario to restart the eocm cn pods")
def step_impl(context):
    restart_pods_eocm()