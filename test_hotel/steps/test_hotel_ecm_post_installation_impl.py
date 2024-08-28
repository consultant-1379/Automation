from behave import step
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import (site_creation_cn, site_creation,
                                                                            vim_registration,
                                                                            fetch_existing_external_network_id,
                                                                            put_runtime_env_file_attr_dict)
from com_ericsson_do_auto_integration_scripts.PROJ_VIM import (sync_proj_tenant_creation, sync_proj_project_creation,
                                                               create_availability_zone, default_sync_proj_id,
                                                               sync_existing_project, sync_proj_vdc_creation)
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import prepare_openrc_files
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core


@step("I start the Scenario to create the site")
def step_impl(context):
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

    if is_cloudnative:
        site_creation_cn(test_hotel=True)
    else:
        site_creation()


@step("I have user inputs for CEE cleanup")
def step_impl(context):
    context.EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    context.ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    context.project_name = context.EPIS_data._EPIS__project_name
    context.openstack_ip = context.EPIS_data._EPIS__openstack_ip
    context.username = context.EPIS_data._EPIS__openstack_username
    context.password = context.EPIS_data._EPIS__openstack_password
    context.openrc_filename = context.EPIS_data._EPIS__openrc_filename
    context.ecm_environment = context.ecm_host_data._Ecm_PI__ECM_Host_Name


@step("I create openrc files for static and dynamic project")
def step_impl(context):
    prepare_openrc_files(context.ecm_environment, context.openrc_filename, context.project_name, context.openstack_ip,
                         context.username, context.password)


@step("I start the Scenario to create sync proj tenant")
def step_impl(context):
    sync_proj_tenant_creation()


@step("I start the Scenario to register the Vim")
def step_impl(context):
    vim_registration(test_hotel=True)


@step("I Start the Scenario to create availability zone")
def step_impl(context):
    create_availability_zone(test_hotel=True)


@step("I start the Scenario to create new sync project")
def step_impl(context):
    sync_proj_project_creation(test_hotel=True)


@step("I start the Scenario to fetch sync proj id")
def step_impl(context):
    default_sync_proj_id()


@step("I start the Scenario to create sync existing project")
def step_impl(context):
    sync_existing_project(test_hotel=True)


@step("I start the Scenario to create sync project VDC")
def step_impl(context):
    sync_proj_vdc_creation(test_hotel=True)


@step("I start the Scenario to fetch the existing provider network id")
def step_impl(context):
    fetch_existing_external_network_id()


@step("I start the Scenario to transfer runtime file with updated value")
def step_impl(context):
    put_runtime_env_file_attr_dict()
