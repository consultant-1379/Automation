from behave import *

from com_ericsson_do_auto_integration_scripts.PROJ_VIM import *
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *


@step("I start the Scenario to create the domain")
def step_impl(context):
    domain_creation()


@step("I start the Scenario to create the site")
def step_impl(context):
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        site_creation_cn()
    else:
        site_creation()



@step("I start the Scenario to register the Vim")
def step_impl(context):
    vim_registration()


@step("I start the Scenario to create the project")
def step_impl(context):
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    vim_type = EPIS_data._EPIS__static_project
    if vim_type=='ORCH_STAGING_N53':
        sync_proj_project_creation()
        default_sync_proj_id()
        sync_existing_project()
    else:
        project_creation()


@step("I start the Scenario to create the virtual data centre")
def step_impl(context):
    vdc_creation()


@step("I start the Scenario to create the block storage")
def step_impl(context):
    create_block_storage()


@step("I start the Scenario to create the key-pair")
def step_impl(context):
    create_key_pair()

@step("I start the Scenario to create the icmp rules")
def step_impl(context):
    icmp_rule()

@step("I start the Scenario to create the internal network")
def step_impl(context):
    create_internal_network()


@step("I start the Scenario to create the external network")
def step_impl(context):
    create_external_network()


@step("I start the Scenario to create the bgw ports")
def step_impl(context):
    create_bgw_ports()


@step("I start the Scenario to EO-CM cerificate install")
def step_impl(context):
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    is_cloudnative=Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        renew_eocm_certs()
    else:
        eocm_ha_certificates()
    