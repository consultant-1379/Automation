from behave import *
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
log = Logger.get_logger('cee_cleanup_impl.py')



@step("I start execution of usecase")
def step_impl(context):
    log.info('Starting script : CEE Cleanup tasks')
    Report_file.add_line('Starting script : CEE Cleanup tasks')



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
    
    prepare_openrc_files(context.ecm_environment,context.openrc_filename,context.project_name, context.openstack_ip,context.username,context.password)
   

@step("I check for project exists in CEE")
def step_impl(context):
    project_exists = check_project_exists(context.openrc_filename, context.project_name, context.openstack_ip, context.username, context.password)
    if project_exists:
        log.info('project exists in CEE')
        context.EPIS_data._EPIS__project_exists = True
    else:
        context.EPIS_data._EPIS__project_exists = False
        log.info('Project '+context.project_name+' does not exists in CEE' )
        Report_file.add_line('Project ' + context.project_name + ' does not exists in CEE')
        log.info('END script : CEE Cleanup tasks')
        Report_file.add_line('END script : CEE Cleanup tasks')

@step("I start the Scenario to deregister vCisco license")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
          de_register_license()
    else:
        log.info('Project does not exists , skipping scenario to deregister vCisco license')
        Report_file.add_line('Project does not exists , skipping scenario to deregister vCisco license')


@step("I start the Scenario to delete stacks from CEE")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
        delete_stacks_from_cee(context.openrc_filename, context.project_name, context.openstack_ip, context.username, context.password)
    else:
        log.info('Project does not exists , skipping Scenario to delete stacks from CEE')
        Report_file.add_line('Project does not exists , skipping Scenario to delete stacks from CEE')

@step("I start the Scenario to delete vm instance from CEE")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
        delete_vm_instance(context.openrc_filename, context.project_name, context.openstack_ip, context.username, context.password)
    else:
        log.info('Project does not exists , skipping Scenario to delete vm instance from CEE')
        Report_file.add_line('Project does not exists , skipping Scenario to delete vm instance from CEE')


@step("I start the Scenario to delete cinder volume from CEE")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
        delete_block_storage(context.openrc_filename, context.project_name, context.openstack_ip, context.username, context.password)
    else:
        log.info('Project does not exists , skipping Scenario to delete cinder volume from CEE')
        Report_file.add_line('Project does not exists , skipping Scenario to cinder volume from CEE')


@step("I start the Scenario to delete networks and ports")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
        delete_port_network(context.project_name,context.openrc_filename,context.openstack_ip,context.username,context.password)

    else:
        log.info('Project does not exists , skipping Scenario to delete networks and ports')
        Report_file.add_line('Project does not exists , skipping Scenario to delete networks and ports')


@step("I start the Scenario to delete flavor from CEE")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
        delete_flavour(context.openrc_filename,context.openstack_ip,context.username,context.password)
    else:
        log.info('Project does not exists , skipping Scenario to delete flavor from CEE')
        Report_file.add_line('Project does not exists , skipping Scenario to delete flavor from CEE')


@step("I start the Scenario to delete project from CEE")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
        delete_project(context.openrc_filename,context.project_name,context.openstack_ip,context.username,context.password)
    else:
        log.info('Project does not exists , skipping Scenario to delete project from CEE')
        Report_file.add_line('Project does not exists , skipping Scenario to delete project from CEE')


@step("I start the Scenario to delete users from CEE")
def step_impl(context):
    if context.EPIS_data._EPIS__project_exists == True:
        delete_users(context.ecm_environment,context.openrc_filename,context.project_name,context.openstack_ip,context.username,context.password)

    else:
        log.info('Project does not exists , skipping Scenario to delete users from CEE')
        Report_file.add_line('Project does not exists , skipping Scenario to delete users from CEE')

@step("I end the execution of tasks")
def step_impl(context):
    log.info('END script : CEE Cleanup tasks')
    Report_file.add_line('END script : CEE Cleanup tasks')