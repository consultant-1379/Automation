# Created by eiaavij at 10/17/2018

from behave import *
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.SHUTDOWN_VM import *
from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *
from com_ericsson_do_auto_integration_utilities.Error_handler import *
import ast
import time

log = Logger.get_logger('deploy_impl.py')
ecm_core_data =Initialization_script.get_model_objects(Initialization_script,'ECM_CORE')
sit_data = SIT_initialization.get_model_objects(SIT_initialization,'SIT')

@when('Login to Server "VNF-LCM"')
def step_impl(context):

    context.ip = ecm_core_data._Ecm_core__VNF_LCM_Servicedb_IP
    context.userID = ecm_core_data._Ecm_core__VNF_LCM_Servicedb_Username
    context.password = ecm_core_data._Ecm_core__VNF_LCM_Servicedb_Password

    log.info('Checking vnflcm password')
    check_vnf_lcm_password(context.ip)

    server_connection = ServerConnection.get_connection(context.ip, context.userID, context.password)

    context.connection = server_connection

@given('I have a command {command}')
def step_impl(context,command):

    log.info('Running the sudo command to check server availability')

@step("I execute the sudo commannd")
def step_impl(context):

    server_Error = ServerConnection.check_Server_Error(context.connection)
    if server_Error:
        Report_file.add_line('Script terminated due to error printed above.')
        log.info('Script terminated due to error printed above.')
        assert False


@step("I fetch the correlation Id")
def step_impl(context):
    context.correlation_id = sit_data._SIT__corelationId


@then("User changes to root User")
def step_impl(context):
    pass

@then("I update the json and yaml file")
def step_impl(context):

    # TODO update json file and put on /root path of ECM server
    context.deploy = 'deploy.json'
    context.vnflaf_cee = 'vnflaf_cee.yaml'
    context.vnflaf_services = 'vnflaf-services.yaml'

    sftp = context.connection.open_sftp()
    sftp.put(context.deploy, f'{SIT.get_base_folder(SIT)}deploy.json')
    sftp.put(context.vnflaf_cee, f'{SIT.get_base_folder(SIT)}vnflaf_cee.yaml')
    sftp.put(context.vnflaf_services, f'{SIT.get_base_folder(SIT)}vnflaf-services.yaml')
    sftp.close()


@given("fetch local dir path")
def step_impl(context):


    context.dir = r'com_ericsson_do_auto_integration_files/vnflaf'


@step('I move dir to path {dir_path}')
def step_impl(context,dir_path):
    
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm
        
    if 'TRUE' == is_vm_vnfm :
    
        vm_vnfm_lcm_repo_directory()
    
    else:
        log.info('Removing old vnflaf package from vnflcm')

        destination_folder = r'/vnflcm-ext/current/vnf_package_repo/vnflaf'
        source_folder = r'com_ericsson_do_auto_integration_files/vnflaf'
        
        command = f'sudo -i rm -rf {destination_folder}'
        stdin, stdout, stderr = context.connection.exec_command(command)
        handle_stderr(stderr, log)
        time.sleep(2)

        #command = f'sudo -i mkdir {destination_folder}'
        #stdin, stdout, stderr = context.connection.exec_command(command)
        #handle_stderr(stderr, log)

        #Server_connection.transfer_folder_local_to_remote(Server_connection, context.ip, context.userID,context.password, source_folder, destination_folder)
        
        ServerConnection.put_folder_scp(context.connection, r'com_ericsson_do_auto_integration_files/vnflaf', '/vnflcm-ext/current/vnf_package_repo/')
        time.sleep(10)
        log.info('folder transferred successfully')

        command = f'sudo chmod 777 -R {destination_folder}'
        stdin, stdout, stderr = context.connection.exec_command(command)
        handle_stderr(stderr, log)


@when('Login to Server "ECM Host Blade server"')
def step_impl(context):
    context.ip = ecm_core_data._Ecm_core__ECM_Host_Blade_IP
    context.userID = ecm_core_data._Ecm_core__ECM_Host_Blade_username
    context.password = ecm_core_data._Ecm_core__ECM_Host_Blade_Password
    server_connection = ServerConnection.get_connection(context.ip, context.userID, context.password)
    context.connection = server_connection


@then("I create the curl command for deploying the package")
def step_impl(context):
    log.info('curl command of deployment')
    curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken: {}' --data @deploy.json 'https://{}/ecm_service/vnfpackages/{}/deploy{}'''.format(context.auth_token, context.core_vm_ip, context.vnfPackage_id,"'")
    context.command = curl
    Report_file.add_line('curl command of deployment ' + curl)

@step("I save the correlation id")
def step_impl(context):

    Report_file.add_mesg('Step 6', 'Deploying Package ', context.output)
    log.info('Saving the correlation id for fetching the vApp id')
    output = ast.literal_eval(context.output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        context.correlation_id = output['correlationId']
        log.info('correlation_id : ' + context.correlation_id)
        Report_file.add_line('correlation_id : ' + context.correlation_id)

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for Deploying the package ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for Deploying the package')
        context.connection.close()
        assert False


    sit_data.set_corelationId(sit_data, context.correlation_id)
    sit_data._SIT__corelationId = context.correlation_id

    
@step("I check the order status of deployed dummy node")
def step_impl(context):
    
    order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, context.connection, context.auth_token, context.core_vm_ip,context.correlation_id, 30)

    if order_status:
        log.info('order status for  node deployment completed  '+context.correlation_id)
        Report_file.add_line('order status for  node deployment completed  ' + context.correlation_id)

    else:
        Report_file.add_line(order_output)
        log.error('order status for  node deployment is errored  '+context.correlation_id)
        Report_file.add_line('order status for  node deployment is errored  ' + context.correlation_id)
        assert False


@then("I create the curl command for fetching the vApp id using correlation id")
def step_impl(context):
    log.info('curl command of fetching vApp id from correlation id')
    curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/v2/orders/{}'''.format(context.auth_token, context.core_vm_ip, context.correlation_id + "'")
    context.command = curl
    Report_file.add_line('curl command of fetching vApp id from correlation id ' + curl)

@step("I save the vApp id")
def step_impl(context):

    log.info('Saving the vApp id')
    command_out = context.output[2:-1:1]
    try:
        command_out = command_out.replace('true', 'True')
        command_out = command_out.replace('false', 'False')
    except:

        log.error('ERROR while updating the command_output')

    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        context.vApp_id = output['data']['order']['orderItems'][0]['deployVnfPackage']['id']
        log.info('vApp_id is : ' + context.vApp_id)
        Report_file.add_line('vApp_id is : ' + context.vApp_id)
        log.info('package deployed successfully. Verifying the Ping Response of external_ip_for_services_vm and status of provisioning and operational')
        log.info(context.vApp_id)
        #TODO log the external_ip_for_services_vm
        Report_file.add_line('Executed the curl command for deploying the package : ' + context.vApp_id)
        Report_file.add_line('Package Deployed successfully. Verifying the Ping Response of external_ip_for_services_vm and status of provisioning and operational')

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for Deploying the package ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for Deploying the package')
        context.connection.close()
        assert False

    sit_data.set_vapp_Id(sit_data, context.vApp_id)
    sit_data._SIT__vapp_Id = context.vApp_id


@then("I create the curl command of verification of deployed package")
def step_impl(context):
    
    log.info('curl command of verification of deployment ')
    curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/vapps/{}'''.format(context.auth_token, context.core_vm_ip, context.vApp_id + "'")
    context.command = curl    
    Report_file.add_line('curl command of verification of deployment ' + curl)

@step("I fetch the external_ip_for_services_vm")
def step_impl(context):
    context.external_ip_for_services_vm = sit_data._SIT__external_ip_for_services_vm

@then("I create the command of pinging the external_ip_for_services_vm")
def step_impl(context):


    cmd = 'ping -w 3 '+context.external_ip_for_services_vm
    context.ping_cmd = cmd

@step("I execute the ping command")
def step_impl(context):

    log.info('Pinging ' +context.external_ip_for_services_vm)
    Report_file.add_line('Pinging ' + context.external_ip_for_services_vm)

    stdin, stdout, stderr = context.connection.exec_command(context.ping_cmd)
    cmd_output = str(stdout.read())
    cmd_error = str(stderr.read())
    response = False
    data_loss = ' 100% packet loss'
    context.cmd_output = cmd_output
    if cmd_output.find(data_loss) == -1:

        response = True
        log.info('Ping Successful ' +cmd_output)
        Report_file.add_line('Ping Successful ' + cmd_output)

    else:

        response = False
        log.info('No Response from Ping ' +cmd_output)
        Report_file.add_line('No Response from Ping ' + cmd_output)

    context.ping_response = response

@then("I verify the deploy usecase")
def step_impl(context):

    Report_file.add_mesg('Step 7', 'Verification of Deployment Use Case ', context.output)
    log.info('Verification of Deployment Use Case')

    command_out = context.output[2:-1:1]
    try:

        command_out = command_out.replace('true', 'True')
        command_out = command_out.replace('false', 'False')
    except:

        log.error('ERROR while updating the command_output')

    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:


        provisioningStatus = output['data']['vapp']['provisioningStatus']
        operationalState = output['data']['vapp']['operationalStatus']

        if 'ACTIVE' == provisioningStatus and 'INSTANTIATED' == operationalState and True == context.ping_response:

            log.info('provisioningStatus is : ' + provisioningStatus)
            log.info('operationalState is : ' + operationalState)
            log.info('Ping Successful')
            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)
            Report_file.add_line('Ping Successful')
            log.info('Verification of package deployment is success')
            Report_file.add_line('Verification of package deployment is successful')

        else:
            log.info('Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response ')
            Report_file.add_line('Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response')
            context.connection.close()
            assert False

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for verification of package deployment ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for verification of package deployment')
        context.connection.close()
        assert False


@step("I fetch the vApp id")
def step_impl(context):
    context.vApp_id = sit_data._SIT__vapp_Id


@when("I wait for completion of task for {duration} seconds")
def step_impl(context,duration):
    sleep_time = 120
    time.sleep(sleep_time)

@when ("I wait 60 seconds for Vapp to come up")
def step_impl(context):
    sleep_time = 60
    time.sleep(sleep_time)


@step("I proceed to fetch the service and db hostname")
def step_impl(context):
    fetch_vnflcm_hostname()
    
@step("I proceed to shutdown the service and db hostname for {project_type}")
def step_impl(context,project_type):
    shutdown_vnflcm_vm(project_type)


@step("I proceed to change db server password for dynamic project")
def step_impl(context):
    change_db_server_password('dynamic')   
    

@step("I proceed to change password for VNF-LCM deployed in static project")
def step_impl(context):
    change_password_first_login('static')    


@step("I proceed to change db server password for static project")
def step_impl(context):
    change_db_server_password('static')
    

   