from behave import *
from com_ericsson_do_auto_integration_scripts.PROJ_VIM import *
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger



log = Logger.get_logger('proj_vim_impl.py')

    

@step("I create sync proj openrc files for static project")
def step_impl(context):
    
    prepare_sync_proj_openrc_files()

@step("I start the Scenario to create sync proj tenant")
def step_impl(context):
    sync_proj_tenant_creation()
     


@step("I start the Scenario to Register sync proj VIM")
def step_impl(context):
    sync_proj_vim_registration()

@step("I Start the Scenario to create availability zone")
def step_impl(context):
    create_availability_zone()
    
@step("I Start the Scenario to do sync capacity")
def step_impl(context):
    proj_sync_capacity()
    
@step("I start the Scenario to create new project")
def step_impl(context):
    sync_proj_project_creation()


@step("I start the Scenario to fetch sync proj id")
def step_impl(context):
    default_sync_proj_id()


@step("I start the Scenario to add project to vim")
def step_impl(context):
    add_project_vim()
    
@step("I start the Scenario to Create sync proj VDC")
def step_impl(context):
    sync_proj_vdc_creation()    

