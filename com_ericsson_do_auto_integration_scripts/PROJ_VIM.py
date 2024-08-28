'''
Created on 10 sep 2019

@author: eshetra

'''
import ast
import random
import time
from packaging import version
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import (update_new_vimzone_file,
                                                                          update_create_new_project_file,
                                                                          update_test_hotel_network_creation,
                                                                          update_test_hotel_subnet)
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities

from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import (get_openstack_user_roles,
                                                                            add_default_user_roles,
                                                                            project_vimObject_Id)
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.Ecm_PI import Ecm_PI

log = Logger.get_logger('PROJ_VIM.py')

new_vimzone_id = ''
new_project_id = ''
new_user_id = ''
new_project_system_id = ''
new_admin_user_id = ''


def create_new_openrc_file(openrc_filename, connection, data_dict):
    log.info('start creating openrc file ' + openrc_filename)

    reference_file = r'com_ericsson_do_auto_integration_files/openrc_demo'
    # reference_file = 'openrc_demo'

    lines = None

    with open(reference_file, 'r') as file_handler:

        lines = file_handler.readlines()

    for line in lines:
        if 'export OS_AUTH_URL=' in line:
            index = lines.index(line)
            lines[index] = 'export OS_AUTH_URL=' + data_dict['vim_url'] + '\n'
        elif 'export OS_TENANT_NAME' in line:
            index = lines.index(line)
            lines[index] = 'export OS_TENANT_NAME="' + data_dict['project'] + '"\n'
        elif 'export OS_USERNAME' in line:
            index = lines.index(line)
            lines[index] = 'export OS_USERNAME="' + data_dict['username'] + '"\n'
        elif 'export OS_PASSWORD' in line:
            index = lines.index(line)
            lines[index] = 'export OS_PASSWORD="' + data_dict['password'] + '"\n'

        elif 'export OS_DOMAIN_NAME' in line:

            if 'v3' in data_dict['vim_url']:
                index = lines.index(line)
                lines[index] = 'export OS_DOMAIN_NAME="Default"\n'
            else:
                index = lines.index(line)
                lines[index] = '#export OS_DOMAIN_NAME="Default"\n'

    with open(reference_file, 'w+') as file_handler:

        file_handler.writelines(lines)

    ServerConnection.put_file_sftp(connection, reference_file, '/root/' + openrc_filename)

    log.info('Finished creating openrc file ' + openrc_filename)


def prepare_sync_proj_openrc_files():
    try:

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

        openstack_ip = EPIS_data._EPIS__openstack_ip

        static_project_name = EPIS_data._EPIS__existing_project_name
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        vim_url = EPIS_data._EPIS__sync_vim_url
        adminUserName = EPIS_data._EPIS__existing_project_admin_username
        adminPassword = EPIS_data._EPIS__existing_project_admin_password
        static_openrc_file = EPIS_data._EPIS__sync_openrc_filename

        connection = ServerConnection.get_connection(openstack_ip, username, password)

        static_project_data = {'project': static_project_name, 'vim_url': vim_url, 'username': adminUserName,
                               'password': adminPassword}

        create_new_openrc_file(static_openrc_file, connection, static_project_data)

        time.sleep(2)

        connection.close()

    except Exception as e:

        log.error('Error in creation of openrc files   ' + str(e))
        Report_file.add_line('Error in creation of openrc files ' + str(e))
        connection.close()
        assert False


def get_new_end_points_data(ecm_output):
    log.info('start collecting end points data from openstack')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password

    openrc_filename = EPIS_data._EPIS__sync_openrc_filename
    end_points_data = []
    service_names = ['keystone', 'nova', 'ceilometer', 'cinder', 'glance', 'heatstack', 'neutron']

    ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

    command = 'dos2unix {}'.format(openrc_filename)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

    command = 'source {}'.format(openrc_filename)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

    for service_name in service_names:

        if service_name == 'heatstack':

            command = '''openstack endpoint list --interface public --service {} | grep -i {} '''.format('heat', 'heat')

        else:

            command = '''openstack endpoint list --interface public --service {} | grep -i {}'''.format(service_name,
                                                                                                        service_name)

        Report_file.add_line('command to get endpoint for service ' + command)

        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        Report_file.add_line('command output ' + str(stdout))

        for scope in ecm_output:

            param_name = scope['paramName']
            if param_name == service_name:
                param_value = scope['paramValue'].split(',')[0]
                test_uri = "/v" + param_value

        for line in stdout:
            try:
                stack_data = line.split('|')
                url = stack_data[7]
                ip_address = url.split('://')[1].split(':')[0]
                port = url.split('://')[1].split(':')[1].split('/')[0]

            except:
                log.info('')

        data = {
            "name": service_name,
            "up": True,
            "vimApiVersion": param_value,
            "ipAddress": ip_address,
            "port": int(port),
            "testUri": test_uri
        }

        end_points_data.append(data)

    ShellHandler.__del__(ShellHandler)
    log.info('finished collecting end points data from openstack')
    return end_points_data


def sync_proj_tenant_creation():
    log.info('start tenant creation')

    epis_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    tenant_name = epis_host_data._EPIS__sync_tenant_name
    tenant_username = epis_host_data._EPIS__sync_tenant_username
    tenant_password = epis_host_data._EPIS__sync_tenant_password
    tenant_type = epis_host_data._EPIS__sync_tenant_type

    if tenant_name == 'ECM':

        log.info('Tenant ECM already present')
        Report_file.add_line('Tenant ECM already present')

    else:

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        file_name = r'new_tenant.json'
        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           'tenantName', tenant_name)
        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name, 'tenantAdmin',
                                                  'userName', tenant_username)
        Json_file_handler.modify_first_level_attr(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name, 'tenantAdmin',
                                                  'password', tenant_password)
        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           'intendedProjectType', tenant_type)

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname, is_ecm=True)

        log.info('creating the tenant using the token for authentication ')
        command = f'curl --insecure https://{core_vm_hostname}/ecm_service/tenants -H "Content-Type: ' \
                  f'application/json" -H "AuthToken:{token}" --data @{file_name} '

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']
        if 'SUCCESS' in requestStatus:
            log.info('Tenant created successfully %s', command_output)

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the tenant %s', command_error)
            connection.close()
            assert False

        connection.close()
        log.info('tenant creation ends')


def sync_proj_vim_registration():
    log.info('start  new vim registration')
    Report_file.add_line('New VIM registration begins...')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

    ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name

    log.info('ecm environment ' + ecm_environment)

    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    command = '''curl --insecure "https://{}/ecm_service/configdata" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
        core_vm_hostname, token)
    log.info('command to get vimzone endpoints from ECM ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    file_name = 'new_vimzone_register_RHOS.json'

    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        data_values = output['data']['configurations']
        end_points = get_new_end_points_data(data_values)

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for creating the vimzone ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for creating the vimzone')
        connection.close()
        assert False

    update_new_vimzone_file(file_name, end_points)

    sftp = connection.open_sftp()
    sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
    sftp.close()

    log.info('creating the vimzone using the token for authentication ')
    Report_file.add_line('creating the vimzone using the token for authentication ')
    curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/vimzones'''.format(
        token, file_name, core_vm_hostname)
    command = curl
    Report_file.add_line('Vim Registration command ' + command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Vim Registration curl output ' + command_output)
    output = ast.literal_eval(command_output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        global new_vimzone_id
        new_vimzone_id = output['data']['vimZone']['id']
        log.info(' new vimzone id is : ' + new_vimzone_id)
        Report_file.add_line('new vim zone id is : ' + new_vimzone_id)
        log.info('Created new vimzone successfully')
        log.info(command_output)
        Report_file.add_line('Executed the curl command for new vimzone registration : ' + command_output)
        Report_file.add_line('Created new vimzone successfully')


    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for creating the new vimzone ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for creating the new vimzone')
        connection.close()
        assert False

    connection.close()
    log.info('new vim registration ends')
    Report_file.add_line('new vim registration ends')


def sync_proj_project_creation(test_hotel=False):
    connection = None
    try:
        log.info('start new project creation')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_PI.get_core_vm_hostname(Ecm_PI)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        file_name = 'createnewProject.json'
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

        if is_cloudnative:
            user_roles = get_openstack_user_roles()
            if 'member' in user_roles:
                add_default_user_roles(connection, 'heat_stack_owner,member')
                update_create_new_project_file(test_hotel, 'member')
            elif '_member_' in user_roles:
                add_default_user_roles(connection)
                update_create_new_project_file(test_hotel, '_member_')
            else:
                log.error("default user role is unknown")
                assert False
        else:
            update_create_new_project_file(test_hotel, '_member_')

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        if test_hotel:
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname, is_ecm=True)
        else:
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('creating the new project using the token for authentication ')
        Report_file.add_line('creating the new project using the token for authentication  ')
        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/projects'''.format(
            token, file_name, core_vm_hostname)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('New Project creation curl output: %s', command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']
            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname,
                                                                         order_id, 10)
            if order_status:
                log.info('Order Status is completed: %s', order_id)
                log.info('Created New project successfully: %s', command_output)
                log.info('order status output: %s', order_output)
                log.info('Fetching New project id from order output ')
                global new_project_system_id
                new_project_system_id = order_output['data']['order']['orderItems'][0]['createProject']['id']
                log.info('new project system id is: %s', new_project_system_id)
                log.info('new project creation ends')
            else:
                log.info('order status output: %s', order_output)
                log.info('Order Status is failed with message mentioned above: %s', order_id)
                assert False

        elif 'ERROR' in requestStatus:
            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the project: %s', command_error)
            assert False

    except Exception as error:
        log.error('project creation failed: %s', str(error))
        assert False
    finally:
        if connection:
            connection.close()


def fetch_sync_proj_id(openrc_filename):
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password

    userName = EPIS_data._EPIS__existing_project_user_username
    adminUserName = EPIS_data._EPIS__existing_project_admin_username
    project_name = EPIS_data._EPIS__existing_project_name

    log.info('start fetching required ID')
    Report_file.add_line('Start fetching required ID for synch input begins...')

    ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

    command = 'dos2unix {}'.format(openrc_filename)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

    command = 'source {}'.format(openrc_filename)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

    command = '''openstack project show {} | grep -w id'''.format(project_name)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
    time.sleep(3)
    log.info(stdout)
    for line in stdout:
        network_data = line.split('|')
        new_project_id = network_data[2].strip()

    command = '''openstack user show {} | grep -w id'''.format(userName)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
    time.sleep(3)
    log.info(stdout)
    for line in stdout:
        network_data = line.split('|')
        new_user_id = network_data[2].strip()

    command = '''openstack user show {} | grep -w id'''.format(adminUserName)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
    time.sleep(3)
    log.info(stdout)
    for line in stdout:
        network_data = line.split('|')
        new_admin_user_id = network_data[2].strip()

    return new_project_id, new_user_id, new_admin_user_id


def default_sync_proj_id():
    global new_project_id
    global new_user_id
    global new_admin_user_id
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openrc_filename = EPIS_data._EPIS__sync_openrc_filename
    new_project_id, new_user_id, new_admin_user_id = fetch_sync_proj_id(openrc_filename)


def verify_project_addition(connection, filename, tenant_name):
    log.info('Start to verify Project Addition')
    Report_file.add_line('Start to verify Project Addition')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname

    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' 'tenantid: {}'  --data @{} https://{}/ecm_service/cmdb/projects/{}/add'''.format(
        token, tenant_name, filename, core_vm_hostname, new_project_system_id)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Verification of Project Addition Command output' + command_output)

    output = ast.literal_eval(command_output[2:-1:1])
    requestStatus = output['status']['reqStatus']
    if 'SUCCESS' in requestStatus:
        log.info('Successfully Verified the Project Addition')
        Report_file.add_line('Successfully Verified the Project Addition')

    else:
        log.error('Error While verifying project Addition')
        Report_file.add_line('Error While verifying project Addition')
        assert False


def get_classic_ecm_version(connection, core_vm_ip, old_version):
    log.info('Start to fetch ECM Version')
    Report_file.add_line('Start to fetch ECM Version')
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)
    command = '''curl --insecure "https://{}/ecm_service/product" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
        core_vm_ip, token)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = command_output[2:-1:1]
    output = ast.literal_eval(command_out)
    requestStatus = output['status']['reqStatus']
    if 'SUCCESS' in requestStatus:
        current_ecmversion = output['data']['productVersion']['coreComponents'][0]['version']
        log.info("Current version of ECM : " + str(current_ecmversion))
        Report_file.add_line("Current version of ECM : " + str(current_ecmversion))

        if version.parse(current_ecmversion) >= version.parse(old_version):
            Report_file.add_line('Its Latest ECM Version ' + current_ecmversion)
            return True
        else:
            Report_file.add_line('Its Old ECM Version ' + old_version)
            return False
    else:
        log.info('Error while fetching ecm version')
        Report_file.add_line('Error while fetching ecm verison')
        assert False


def add_project_vim():
    log.info('start adding project to vim creation')
    Report_file.add_line('start adding project to vim begins...')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    epis_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password

    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    tenant_name = epis_host_data._EPIS__sync_tenant_name

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    project_name = EPIS_data._EPIS__existing_project_name
    adminUserName = EPIS_data._EPIS__existing_project_admin_username
    adminPassword = EPIS_data._EPIS__existing_project_admin_password
    userName = EPIS_data._EPIS__existing_project_user_username
    userPassword = EPIS_data._EPIS__existing_project_user_password

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    old_version = '20.0.0.0.2005.1444'
    ecmverison = get_classic_ecm_version(connection, core_vm_ip, old_version)

    if ecmverison == True:
        file_name = r'project_vim.json'

        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'vimZoneId',
                                                   new_vimzone_id)
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'vimObjectId',
                                                   new_project_id)
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'userVimObjectId',
                                                   new_user_id)

        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0,
                                                   'adminUserVimObjectId', new_admin_user_id)
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'localName',
                                                   project_name)
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'localDomainName',
                                                   'Default')

        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimZoneConnections', 0, 'localUserCredentials'], 'userName', userName)
        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimZoneConnections', 0, 'localUserCredentials'], 'userPassword',
                                               userPassword)

        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimZoneConnections', 0, 'localUserCredentials', 'grantedRoles', 0],
                                               'roleName', '_member_')
        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimZoneConnections', 0, 'localUserCredentials', 'grantedRoles', 1],
                                               'roleName', 'heat_stack_owner')

        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimZoneConnections', 0, 'localAdminUserCredentials'], 'adminUserName',
                                               adminUserName)
        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimZoneConnections', 0, 'localAdminUserCredentials'], 'adminPassword',
                                               adminPassword)

        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimZoneConnections', 0, 'localAdminUserCredentials', 'grantedRoles',
                                                0], 'roleName', 'admin')

    else:
        file_name = r'project_vim_old.json'
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'vimZoneId',
                                                   new_vimzone_id)
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'vimObjectId',
                                                   new_project_id)
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name,
                                                   'vimZoneConnections', 0, 'userVimObjectId',
                                                   new_user_id)

    sftp = connection.open_sftp()
    sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
    sftp.close()

    verify_project_addition(connection, file_name, tenant_name)
    connection.close()


def update_sync_proj_createvdc_file(file_name):
    try:
        log.info('Start to update create_sync_proj_vdc.json file ')
        Report_file.add_line('Start to update create_sync_proj_vdc.json file')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

        tenant = EPIS_data._EPIS__sync_tenant_name
        vimzone_name = EPIS_data._EPIS__sync_vimzone_name
        vdc_name = vimzone_name + '_vdc'

        log.info('Going  to create vdc with name  ' + vdc_name)
        Report_file.add_line('Going  to create vdc with name  ' + vdc_name)

        vdc_data = {
            "name": vdc_name,
            "vimZones": [
                vimzone_name
            ],
            "description": "Datacenter for demo"
        }

        data = {'tenantName': tenant, 'vdc': vdc_data}
        Json_file_handler.modify_list_of_attributes(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/' + file_name, data)
        log.info('Finished to update create_sync_proj_vdc.json file ')
        Report_file.add_line('Finished to update create_sync_proj_vdc.json file')

    except Exception as e:

        log.error('Error while updating create_sync_proj_vdc.json file ' + str(e))
        Report_file.add_line('Error while updating create_sync_proj_vdc.json file ,check logs for more details')
        assert False


def sync_proj_vdc_creation(test_hotel=False):
    try:

        log.info('start SYNC PROJ VDC creation')
        Report_file.add_line('VDC creation begins...')
        log.info('waiting 90 seconds till project come up successfully')
        time.sleep(90)
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        epis_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_core_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        enviornment = ecm_core_data._Ecm_core__enviornment

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        file_name = r'create_sync_proj_vdc.json'
        update_sync_proj_createvdc_file(file_name)

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        token = Common_utilities.sync_proj_authToken(Common_utilities, connection, core_vm_hostname)
        log.info('creating the VDC using the token for authentication ')

        Report_file.add_line('creating the VDC using the token for authentication  ')

        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/vdcs'''.format(
            token, file_name, core_vm_hostname)

        command = curl
        Report_file.add_line('VDC creation curl  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('VDC creation curl output  ' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname,
                                                                         order_id, 10)

            if order_status:

                log.info('Order Status is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info('Created SYNC PROJ VDC successfully using the token for authentication ')
                log.info('Created SYNC PROJ VDC successfully :  ' + command_output)
                Report_file.add_line('Executed the curl command for VDC creation :  ' + command_output)
                Report_file.add_line('Created VDC successfully')
                log.info(order_output)
                log.info('Fetching SYNC PROJ VDC ID ')
                Report_file.add_line('Fetching VDC ID')
                vdc_id = order_output['data']['order']['orderItems'][0]['createVdc']['id']
                vdc_name = order_output['data']['order']['orderItems'][0]['createVdc']['name']
                log.info('Fetched VDC ID :' + vdc_id)
                epis_host_data._EPIS__vdc_id = vdc_id
                Report_file.add_line('Executed the curl command for Fetching VDC ID :  ' + command_output)
                Report_file.add_line('Fetched VDC ID :' + vdc_id)

                data_file = r'com_ericsson_do_auto_integration_files/run_time_' + enviornment + '.json'
                dest = r'/root/' + 'run_time_' + enviornment + '.json'
                ServerConnection.get_file_sftp(connection, dest, data_file)

                if test_hotel:

                    Json_file_handler.modify_attribute(Json_file_handler, data_file, 'VDC_ID', vdc_id)
                    Json_file_handler.modify_attribute(Json_file_handler, data_file, 'VDC_NAME', vdc_name)

                else:

                    Json_file_handler.modify_attribute(Json_file_handler, data_file, 'SYNC_PROJ_VDC_ID', vdc_id)
                    Json_file_handler.modify_attribute(Json_file_handler, data_file, 'SYNC_PROJ_VDC_NAME', vdc_name)

                ServerConnection.put_file_sftp(connection, data_file, dest)

            else:

                log.info(order_output)
                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the SYNC PROJ VDC ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for creating the SYNC PROJ VDC')
            connection.close()
            assert False

        connection.close()
        log.info('SYNC PROJ VDC creation ends')
        Report_file.add_line('SYNC PROJ VDC creation ends...')

    except Exception as e:

        log.error('Error while updating createvdc.json file ' + str(e))
        Report_file.add_line('Error while updating createvdc.json file ,check logs for more details')
        assert False


def update_add_availability_zone_file(filename, new_vimzone_id, name):
    try:

        file_path = r'com_ericsson_do_auto_integration_files/' + filename

        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'vimZoneId', new_vimzone_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_path, [], 'name', name)

    except Exception as e:
        log.error('Error while updating ' + filename + ' ' + str(e))
        Report_file.add_line('Error while updating ' + filename + ' ' + str(e))
        assert False


def execute_add_availability_zone_cmd(connection, test_hotel):
    core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

    if test_hotel:

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname, is_ecm=True)

    else:

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    command = '''curl --insecure "https://{}/ecm_service/availabilityzones/" -H "Accept: application/json" -H "Content-Type: application/json" -H "AuthToken: {}" --data @addAZ.json'''.format(
        core_vm_hostname, token)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)

    output = ast.literal_eval(command_output[2:-1:1])
    requestStatus = output['status']['reqStatus']
    if 'SUCCESS' in requestStatus:
        log.info('Successfully Verified the Project Addition')
        Report_file.add_line('Successfully Verified the Project Addition')
        availabilityzone_id = output['data']['availabilityZone']['id']
        log.info('Availability Zone ID - ' + availabilityzone_id)
        name = output['data']['availabilityZone']['name']
        log.info('Availability Zone Name - ' + name)
    else:
        log.error('Failed to create availability zone')
        Report_file.add_line('failed to create availability zone')
        assert False


def create_availability_zone(test_hotel=False):
    try:
        log.info('Start to add availability zone')
        Report_file.add_line('Start to add availability zone')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        filename = 'addAZ.json'
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        syncvimavailabilityzones = EPIS_data._EPIS__sync_vim_availability_zone
        availability_zone_list = syncvimavailabilityzones.split(',')

        for zone_name in availability_zone_list:
            if 'nova' == zone_name:
                log.info('Nova in the list , skipping addition of Nova AZ')
            else:
                if test_hotel:
                    vimzone_id = sit_data._SIT__vimzone_id

                else:
                    vimzone_id = new_vimzone_id

                update_add_availability_zone_file(filename, vimzone_id, zone_name)
                ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + filename,
                                               SIT.get_base_folder(SIT) + filename)
                execute_add_availability_zone_cmd(connection, test_hotel)

    except Exception as e:

        log.info('Failed to create sync vim availability zone' + str(e))
        Report_file.add_line('Failed to create sync vim availability zone' + str(e))
        assert False


def proj_sync_capacity():
    try:
        log.info('start executing curl command to project sync VIM capacity')
        Report_file.add_line('start executing curl command to project sync VIM capacity')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        new_vim_name_for_cloud = EPIS_data._EPIS__sync_vimzone_name
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        filename = 'empty.json'
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + filename,
                                       SIT.get_base_folder(SIT) + filename)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        command = '''curl --insecure "https://{}/ecm_service/vimzones/ecm-vim-capacity-sync-service/synchronize-capacity/{}" -H "Accept: application/json" -H "Content-Type: application/json" -H "AuthToken: {}" --data empty.json'''.format(
            core_vm_hostname, new_vim_name_for_cloud, token)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        log.info(command_output)
        requestStatus = output['status']['reqStatus']
        if 'SUCCESS' in requestStatus:
            log.info('Successfully Verified the Project Addition')
            Report_file.add_line('Successfully Verified the Project Addition')

        else:
            log.error('Error While verifying project Addition')
            Report_file.add_line('Error While verifying project Addition')
            assert False
    except Exception as e:

        log.info('Failed to execute project sync vim capacity' + str(e))
        Report_file.add_line('Failed to create project sync vim capacity' + str(e))
        assert False


def update_register_proj_file(file_name):
    try:

        log.info('Start to update ' + file_name + ' file')
        Report_file.add_line('Start to update ' + file_name + ' file')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        adminPassword = EPIS_data._EPIS__existing_project_admin_password
        userPassword = EPIS_data._EPIS__existing_project_user_password
        vimzone_id = sit_data._SIT__vimzone_id

        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name, 'vimProjects',
                                                   0, 'vimObjectId',
                                                   new_project_id)
        Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                   'com_ericsson_do_auto_integration_files/' + file_name, 'vimProjects',
                                                   0, 'vimZoneId', vimzone_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimProjects', 0, 'userCredentials'],
                                               'userPassword', userPassword)

        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimProjects', 0, 'userCredentials'],
                                               'vimObjectId', new_user_id)
        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimProjects', 0, 'adminUserCredentials'],
                                               'adminPassword', adminPassword)
        Json_file_handler.update_any_json_attr(Json_file_handler, 'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['vimProjects', 0, 'adminUserCredentials'],
                                               'vimObjectId', new_admin_user_id)



    except Exception as e:
        log.error('Error while updating ' + file_name + ' file ' + str(e))
        Report_file.add_line('Error while updating ' + file_name + ' file ,check logs for more details')
        assert False


def sync_existing_project(test_hotel=False):
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if test_hotel:

            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname, is_ecm=True)

        else:

            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        filename = 'register_proj.json'
        update_register_proj_file(filename)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + filename,
                                       SIT.get_base_folder(SIT) + filename)

        command = '''curl --insecure "https://{}/ecm_service/projects/{}/register" -H "Content-Type: application/json" -H "AuthToken:{} " --data @{}'''.format(
            core_vm_hostname, new_project_system_id, token, filename)
        Report_file.add_line('Command - ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        log.info(command_output)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']
            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname,
                                                                         order_id, 10)

            if order_status:
                log.info('Order Status is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info(order_output)
                log.info('Sync Existing Project creation has been Success.')
                Report_file.add_line('Sync Existing Project creation has been Success.')
                log.info('fetching the project vim object id.')
                project_vimObject_Id(connection, core_vm_hostname, new_project_system_id, token, test_hotel=True)
            else:
                log.info(order_output)
                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                assert False
        else:
            log.info('Failed to create Sync existing Project')
            Report_file.add_line('Failed to create Sync existing Project')
            assert False

    except Exception as e:
        log.error('Error while creating Sync Existing project')
        Report_file.add_line('Error while creating Sync Existing project')
        assert False

    finally:
        connection.close()


def add_test_hotel_subnet(connection, network_id, core_vm_hostname, token):
    """Creation of Test Hotel External Network Subnet (SM-139387)"""
    try:
        log.info('Creating test hotel subnet')
        file_name = 'test_hotel_subnet.json'
        update_test_hotel_subnet(file_name, network_id)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        command = f'curl -X POST --insecure --header "Content-Type: application/json" --header "Accept: application/json" --header "AuthToken:{token}" --data @{file_name} https://{core_vm_hostname}/ecm_service/cmdb/subnets'

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            network_subnet_id = output['data']['subnet']['id']
            log.info('network subnet id created successfully: %s', network_subnet_id)

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the test hotel subnet: %s', command_error)
            assert False

    except Exception as e:
        log.error('Error while creating test hotel subnet %s', str(e))
        assert False


def add_test_hotel_external_network():
    """Creation of Test Hotel External Network (SM-139387)"""
    connection = None
    try:

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        file_name = 'test_hotel_network.json'
        update_test_hotel_network_creation(file_name)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/test_hotel/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname, is_ecm=True)
        command = f'curl -X POST --insecure --header "Content-Type: application/json" --header "Accept: application/json" --header "AuthToken:{token}" --data @{file_name} https://{core_vm_hostname}/ecm_service/v2/cmdb/vns'

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            external_network_id = output['data']['vn']['id']
            log.info('external network id created successfully: %s', external_network_id)
            add_test_hotel_subnet(connection, external_network_id, core_vm_hostname, token)

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the test hotel external network: %s', command_error)
            assert False


    except Exception as e:
        log.error('Error while creating test hotel external network %s', str(e))
        assert False

    finally:
        connection.close()
