# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************

'''
Created on 10 sep 2018

@author: eshetra

'''
import base64
import ipaddress
import random
import time
import os
import ast
from packaging import version
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import (
    update_create_site_file, update_dev_stack_vimzone_file, update_create_project_file,
    update_createvdc_file, update_blockStorage_file, get_network_details, update_vimzone_file,
    update_external_network_creation_file, update_internal_network_creation_file)
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.MYSQL_DB import get_PSQL_connection, check_record_exits_mySQL_table
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.EPIS import EPIS
from com_ericsson_do_auto_integration_model.Ecm_PI import Ecm_PI
from com_ericsson_do_auto_integration_model.SIT import SIT


log = Logger.get_logger('ECM_POST_INSTALLATION')

vimzone_id = ''
data_file = ''
runtime_file = ''
global runtime_attr_dict
runtime_attr_dict = {}


def initialize_user_input(user_input_file):
    ECM_PI_Initialization.store_user_inputs(ECM_PI_Initialization, user_input_file)


def domain_creation():
    log.info('start domain creation')
    Report_file.add_line('Domain creation begins...')

    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType

    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    # ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    log.info('creating the domain using the token for authentication ')

    file_name = 'domain.json'
    if cloud_type == 'CEE':
        domain_name = 'CEE'
    else:
        domain_name = 'Default' + '_' + str(random.randint(0, 999))
    domain_data = {"name": domain_name, "description": "Automation Script Domain"}
    Json_file_handler.update_json_file(Json_file_handler,
                                       r'com_ericsson_do_auto_integration_files/' + file_name,
                                       domain_data)

    sftp = connection.open_sftp()
    sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
    sftp.close()

    curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/domains{}'''.format(
        token, file_name, core_vm_hostname, "'")
    command = curl
    Report_file.add_line('Domain creation command ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('domain creation curl output ' + command_output)

    output = ast.literal_eval(command_output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        domain_id = output['data']['domain']['id']
        log.info('domain name:' + domain_name + ' with id ' + domain_id)
        Report_file.add_line('domain name:' + domain_name + 'with id ' + domain_id)
        log.info('domain created successfully')
        Report_file.add_line('Executed the curl command for creation of domain : ' + domain_name)
        Report_file.add_line('Created Domain successfully')

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for creating the domain ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for creating the domain')
        connection.close()
        assert False


def site_creation():
    log.info('start site creation')
    Report_file.add_line('site creation begins...')
    update_create_site_file()
    core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    site_name = EPIS_data._EPIS__site_name
    username = core_vm_data._Ecm_PI__CORE_VM_USERNAME
    password = core_vm_data._Ecm_PI__CORE_VM_PASSWORD
    deployment_type = core_vm_data._Ecm_PI__deployment_type

    rdb_vm_ip = core_vm_data._Ecm_PI__RDB_VM_IP

    if deployment_type == 'HA':
        core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
    else:
        core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP

    cmdb_password = Common_utilities.fetch_cmdb_password(Common_utilities)

    log.info('Check if site already exists or not ')

    db_connection = get_PSQL_connection(rdb_vm_ip, 'ecmdb1', 'cmdb', cmdb_password)

    site_exists = check_record_exits_mySQL_table(db_connection, 'cm_site', 'name', site_name)

    if True == site_exists:

        log.info('site already exists with name ' + site_name)
        Report_file.add_line('site already exists with name ' + site_name)

    else:
        log.info('site does not exists with name ' + site_name)
        log.info('removing old entry of core_vm from host file')

        os_command = 'ssh-keygen -R {}'.format(core_vm_ip)
        os.system(os_command)

        connection = ServerConnection.get_connection(core_vm_ip, username, password)

        fileExists = ServerConnection.file_exists(core_vm_ip, username, password,
                                                  '/app/ecm/tools/cmdb/cmdb-util/data/samples/CreateSite.yaml')

        if fileExists:
            command = 'cd /app/ecm/tools/cmdb/cmdb-util/data/samples/ ; cp CreateSite.yaml CreateSite.yaml.orig'
            stdin, stdout, stderr = connection.exec_command(command)
            Report_file.add_mesg('Step 1 ', 'Backup of CreateSite.yaml done', command)

        file_name = 'com_ericsson_do_auto_integration_files/CreateSite.yaml'

        sftp = connection.open_sftp()
        sftp.put(file_name, '/app/ecm/tools/cmdb/cmdb-util/data/samples/CreateSite.yaml')
        sftp.close()
        Report_file.add_mesg('Step 2 ', 'updated CreateSite.yaml',
                             '/app/ecm/tools/cmdb/cmdb-util/data/samples/CreateSite.yaml')
        log.info('updated  CreateSite.yaml file  ')

        log.info('giving 777 permission to createSite.yaml file for access of other user')
        command = 'chmod 777 /app/ecm/tools/cmdb/cmdb-util/data/samples/CreateSite.yaml'
        stdin, stdout, stderr = connection.exec_command(command)
        time.sleep(2)
        log.info('permission given to createsite.yaml')

        siteadd = '''./cmdbUpdate.sh -filename /app/ecm/tools/cmdb/cmdb-util/data/samples/CreateSite.yaml -mode commit -username cmdb -password {} -logLevel DEBUG'''.format(
            cmdb_password)

        interact = connection.invoke_shell()
        command = 'su ecm_admin'
        interact.send(command + '\n')
        time.sleep(2)

        command = 'cd /app/ecm/tools/cmdb/cmdb-util/util'
        interact.send(command + '\n')
        time.sleep(2)

        command = siteadd
        interact.send(command + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if 'want to continue (y/n)' in buff:
            command = 'y'
            interact.send(command + '\n')
            time.sleep(15)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

        Report_file.add_line('Site creation curl output ' + buff)
        interact.shutdown(2)
        if 'Exit Code: 0' in buff:
            log.info('Created Site successfully')
            Report_file.add_line('Created Site successfully')

        else:
            log.error('Site Creation Failed. Check the logs under /app/ecm/tools/cmdb/cmdb-util/logs')
            Report_file.add_line(
                'Site Creation Failed. Check the logs under /app/ecm/tools/cmdb/cmdb-util/logs')
            log.error('Script terminated : Site Creation Failed')
            Report_file.add_line('Script terminated : Site Creation Failed')
            connection.close()
            assert False

        log.info('Site creation ends')
        Report_file.add_line('SITE creation ends...')

        connection.close()


def site_creation_cn(test_hotel=False):
    connection = None
    try:

        log.info("Start to Create Site Creation on EO-CM")

        log.info('Check if site already exists or not')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = Ecm_core.get_ecm_host_blade_ip(Ecm_core)
        ecm_username = Ecm_core.get_ecm_host_blade_username(Ecm_core)
        ecm_password = Ecm_core.get_ecm_host_blade_password(Ecm_core)

        ecm_gui_username = Ecm_core.get_ecm_gui_username(Ecm_core)
        ecm_gui_password = Ecm_core.get_ecm_gui_password(Ecm_core)

        ecm_fqdn = Ecm_core.get_core_vm_hostname(Ecm_core)

        site_name = EPIS.get_site_name(EPIS)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if test_hotel:

            token = Common_utilities.authToken(Common_utilities, connection, ecm_fqdn, is_ecm=True)

        else:

            token = Common_utilities.authToken(Common_utilities, connection, ecm_fqdn)

        site_exists = check_site_exits(connection, token, ecm_fqdn, site_name)

        if True == site_exists:

            log.info('site already exists with name: %s', site_name)

        else:
            log.info('site does not exists with name: %s', site_name)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            file_name = 'com_ericsson_do_auto_integration_files/CreateSite.yaml'

            log.info('Creating site using file: %s', file_name)
            update_create_site_file()
            sftp = connection.open_sftp()
            sftp.put(file_name, SIT.get_base_folder(SIT)+'CreateSite.yaml')
            sftp.close()

            auth_basic = base64.b64encode(bytes(ecm_gui_username + ':' + ecm_gui_password, encoding='utf-8'))
            decoded_auth_basic = auth_basic.decode('utf-8')
            log.info(decoded_auth_basic)

            command = '''curl -X POST --header 'Authorization:Basic {}' --header 'tenantId:ECM' --insecure https://{}/ecm_service/cmdb/dbutils/cmdbupdate -F 'files=@CreateSite.yaml' -F "mode=COMMIT"'''.format(
                decoded_auth_basic, ecm_fqdn)

            log.info('Site creation command: %s', command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            log.info('Site creation command output: %s', command_output)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            output = ast.literal_eval(command_out)
            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:

                log.info("Successfully created the site")

            elif 'ERROR' in requestStatus:

                command_error = output['status']['msgs'][0]['msgText']

                log.error('Error executing curl command for creating the site %s', command_error)

                assert False

    except Exception as error:
        log.error('Error failed to create site: %s', str(error))
        assert False

    finally:
        connection.close()


def check_site_exits(connection, token, ecm_fqdn, site_name):
    command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/sites'''.format(
        token, ecm_fqdn)
    log.info('command to get site : %s', command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    log.info('Command output: %s', command_out)
    command_out = ast.literal_eval(command_out)
    requestStatus = command_out['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        if 'data' in command_out:
            output = command_out["data"]["sites"]
            for site in output:
                name = site['name']

                if site_name == name:
                    return True

        return False

    elif 'ERROR' in requestStatus:

        command_error = command_out['status']['msgs'][0]['msgText']
        log.error('Error executing curl command for getting the site name command :  %s', command_error)
        connection.close()
        assert False


def check_if_vimurl_contain_cloud7a():
    try:
        log.info('Start to check if VIM URL contain cloud7a')
        Report_file.add_line('Start to check if VIM URL contain cloud7a')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        vim_url = EPIS_data._EPIS__vim_url
        if 'cloud7a' in vim_url:
            Report_file.add_line('Cloud7a exist in the vim url value')
            return True
        else:
            return False
    except Exception as e:

        log.error('Error while Checking vim url contains cloud7a or not  ' + str(e))
        Report_file.add_line('Error while Checking vim url contains cloud7a or not' + str(e))
        assert False


def get_openstack_user_roles():
    """
    Collect user roles present in openstack(Identity->Roles)
    Returns: {<Name>: <ID>,..}
    Example output:
    {'creator': '12d5370514de4cd6ac77249eafe16216', 'heat_stack_owner': '3b7defd55cfa48b39938064d621dd8e4'
     '_member_': '9fe2ff9ee4384b1894a90878d3e92bab' ..}
    """
    try:
        log.info('start collecting user roles from openstack')
        openstack_ip, username, password, _ = \
            Server_details.openstack_host_server_details(Server_details)
        ecm_environment = Ecm_PI.get_ecm_host_name(Ecm_PI)
        openrc_filename = 'openrcauto_' + ecm_environment
        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'dos2unix {}'.format(openrc_filename)
        ShellHandler.execute(ShellHandler, command)
        command = 'source {}'.format(openrc_filename)
        ShellHandler.execute(ShellHandler, command)
        command = 'openstack role list -f value'
        log.info('command to get user roles from openstack: %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info('command output: %s', str(stdout))
        output = {elem.strip('\n').split()[1]: elem.strip('\n').split()[0] for elem in stdout}
        log.info('parsed output for user roles from openstack: %s', output)
        return output
    except Exception as error:
        log.error('Error in collecting user roles from openstack: %s', str(error))
        assert False


def get_end_points_data(ecm_output, ecm_environment):
    log.info('start collecting end points data from openstack')
    openstack_ip, username, password, _ = Server_details.openstack_host_server_details(Server_details)
    openrc_filename = 'openrcauto_' + ecm_environment
    end_points_data = []
    service_names = ['keystone', 'nova', 'ceilometer', 'cinder', 'glance', 'heatstack', 'neutron']

    ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

    command = 'dos2unix {}'.format(openrc_filename)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

    command = 'source {}'.format(openrc_filename)
    stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

    for service_name in service_names:
        if service_name == 'heatstack':
            command = '''openstack endpoint list --interface public --service {} | grep -i {} '''.format(
                'heat', 'heat')
        else:
            command = '''openstack endpoint list --interface public | grep -i {}'''.format(service_name)

        Report_file.add_line('command to get endpoint for service ' + command)
        log.info('command to get endpoint for service %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        Report_file.add_line('command output ' + str(stdout))
        log.info('command output %s', str(stdout))

        if not stdout:
            continue

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

                if service_name == 'glance':
                    log.info('Updating the image url in run time file')
                    auth_url = '''https://{}:{}{}'''.format(ip_address, port.strip(), '/v2')
                    log.info('Image url :%s', auth_url)
                    runtime_attr_dict['IMAGE_AUTH_URL'] = auth_url
            except Exception as error:
                log.error('Failed to fetch endpoint details: %s', str(error))

        if service_name == 'glance':
            data = {
                "name": service_name,
                "up": True,
                "vimApiVersion": "2.0",
                "ipAddress": ip_address,
                "port": int(port),
                "testUri": "/v2.0"
            }

        else:
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


def check_vimzone_exist(connection, token, core_vm_hostname, vim_zone_name):
    command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/vimzones'''.format(
        token, core_vm_hostname)
    log.info('command to get vimzone name ' + command)
    Report_file.add_line('command to get vimzone name ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    command_out = ast.literal_eval(command_out)
    requestStatus = command_out['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        if 'data' in command_out:
            output = command_out["data"]["vimZones"]
            for vimzone_data in output:
                name = vimzone_data['name']
                if vim_zone_name == name:
                    id = vimzone_data['id']

                    return True, id

        return False, ''

    elif 'ERROR' in requestStatus:

        command_error = command_out['status']['msgs'][0]['msgText']
        log.error('Error executing curl command for getting the vimzone name command :  ' + command_error)
        Report_file.add_line('Error executing curl command for getting the vimzone name command :  ')
        Report_file.add_line(command_error)
        connection.close()
        assert False


def vim_registration(test_hotel=False):
    log.info('start vim registration')
    Report_file.add_line('VIM registration begins...')

    ecm_environment = Ecm_PI.get_ecm_host_name(Ecm_PI)
    log.info('ecm environment %s', ecm_environment)
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    core_vm_hostname = Ecm_PI.get_core_vm_hostname(Ecm_PI)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    vim_zone_name = EPIS.get_vimzone_name(EPIS)

    if test_hotel:
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname, is_ecm=True)
    else:
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    log.info('Checking if vimzone already exists.')
    Report_file.add_line('Checking if vimzone already exists.')
    vimzone_exists = check_vimzone_exist(connection, token, core_vm_hostname, vim_zone_name)

    if vimzone_exists[0]:
        log.info('vimzone already exists with name %s', vim_zone_name)
        Report_file.add_line('vimzone already exists with name ' + vim_zone_name)
        global vimzone_id
        vimzone_id = vimzone_exists[1]
        log.info('vimzone id  %s', vimzone_id)
        runtime_attr_dict['VIMZONE_ID'] = vimzone_id

    else:
        log.info('vimzone does not exists with name %s', vim_zone_name)
        if 'Devstack' in ecm_environment:
            file_name = 'testHotel_Devstack.json'
            update_dev_stack_vimzone_file(file_name)
        else:
            file_name = 'vimzone_register.json'
            command = '''curl --insecure "https://{}/ecm_service/configdata" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
                core_vm_hostname, token)
            log.info('command to get vimzone endpoints from ECM: %s', command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            output = ast.literal_eval(command_out)
            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:
                data_values = output['data']['configurations']
                end_points = get_end_points_data(data_values, ecm_environment)
                update_vimzone_file(file_name, end_points)

            elif 'ERROR' in requestStatus:
                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for creating the vimzone: %s', command_error)
                connection.close()
                assert False

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        log.info('creating the vimzone using the token for authentication ')
        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/vimzones'''.format(
            token, file_name, core_vm_hostname)
        command = curl
        log.info('Vim Registration command %s', command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('Vim Registration curl output: %s', command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            vimzone_id = output['data']['vimZone']['id']
            SIT.set_vimzone_id(SIT, vimzone_id)
            log.info('vimzone id is : %s', vimzone_id)
            log.info('Created vimzone successfully')

            runtime_attr_dict['VIMZONE_ID'] = vimzone_id
        elif 'ERROR' in requestStatus:
            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the vimzone: %s', command_error)
            connection.close()
            assert False

        connection.close()
        log.info('vim registration ends')


def ram_vcpu_size(vimObjectId):
    try:

        log.info('Increasing the Ram and vCPU size ')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openrc_filename = EPIS_data._EPIS__openrc_filename
        environment = ecm_host_data._Ecm_PI__ECM_Host_Name

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = 'openstack quota set --ram {} {}'.format(EPIS.get_ram_cpu_storage(EPIS).split(',')[0], vimObjectId)
        log.info('Command to set Ram size %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        command = 'openstack quota set --cores {} {}'.format(EPIS.get_ram_cpu_storage(EPIS).split(',')[1], vimObjectId)
        log.info('Command to set vCPU size %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        log.info('Ram and vCPU size increased')

        log.info('Setting quota for subnets, networks, instances and  ports')

        command = 'openstack quota set --subnets 40 {}'.format(vimObjectId)
        log.info('Command to set subnets %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        command = 'openstack quota set --networks 40 {}'.format(vimObjectId)
        log.info('Command to set networks %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        command = 'openstack quota set --instances 30 {}'.format(vimObjectId)
        log.info('Command to set instances %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        command = 'openstack quota set --ports 150 {}'.format(vimObjectId)
        log.info('Command to set vCPU size %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        command = 'openstack quota set --secgroup-rules 300 {}'.format(vimObjectId)
        log.info('Command to set security group rules %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        command = 'openstack quota set --secgroups 50 {}'.format(vimObjectId)
        log.info('Command to set security group %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        command = 'openstack quota set --gigabytes {} {}'.format(EPIS.get_ram_cpu_storage(EPIS).split(',')[2],
                                                                 vimObjectId)
        log.info('Command to set gigabyte %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        log.info('Finished Setting quota for subnets, networks, instances ,  ports and security rules')

        log.info('increasing injected-file-size for ECDE 3pp usecase')

        command = 'openstack quota set --injected-file-size 1024000 {}'.format(vimObjectId)
        log.info('Command to set injected-file-size %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(5)

        log.info('Finished increasing injected-file-size for ECDE 3pp usecase')

        ShellHandler.__del__(ShellHandler)

    except Exception as e:

        ShellHandler.__del__(ShellHandler)
        log.error('Error in Increasing the Ram and vCPU size %s', str(e))
        log.error('Error in Setting quota for subnets, networks, instances and  ports')
        assert False


def check_project_exist(connection, token, core_vm_hostname, project_name):
    command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/projects'''.format(
        token, core_vm_hostname)
    log.info('command to get project : ' + command)
    Report_file.add_line('command to get project : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    command_out = ast.literal_eval(command_out)
    requestStatus = command_out['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        if 'data' in command_out:
            output = command_out["data"]["projects"]
            for project_data in output:
                name = project_data['name']

                if project_name == name:
                    project_id = project_data['id']
                    for vim_object_id in project_data['vimZoneConnections']:
                        vimObjectId = vim_object_id['vimObjectId']
                    return True, project_id, vimObjectId

        return False, '', ''

    elif 'ERROR' in requestStatus:

        command_error = command_out['status']['msgs'][0]['msgText']
        log.error('Error executing curl command for getting the project name command :  ' + command_error)
        Report_file.add_line('Error executing curl command for getting the project name command :  ')
        Report_file.add_line(command_error)
        assert False


def project_vimObject_Id(connection, core_vm_hostname, project_id, token, test_hotel=False):
    log.info('start fetching vim object id for Project')
    log.info('wait 5 seconds to complete the project vimobject id ')
    time.sleep(5)
    curl = '''curl --insecure 'https://{}/ecm_service/projects/{}' -H 'AuthToken: {}' -H 'Accept: application/json{}'''.format(
        core_vm_hostname, project_id, token, "'")
    command = curl
    Report_file.add_line('Project vim object id curl ' + command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Project vim object id output' + command_output)

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        vimObjectId = output['data']['project']['vimZoneConnections'][0]['vimObjectId']
        projectid = output['data']['project']['id']
        log.info('project vim object id is  :' + vimObjectId)
        Report_file.add_line('project vim object id is  :' + vimObjectId)
        Report_file.add_line('project  id is  :' + projectid)

        runtime_attr_dict['CEE_TENANT_ID'] = vimObjectId
        runtime_attr_dict['PROJECT_ID'] = projectid

        if test_hotel:

            log.info('Test hotel , skipping changing the ram cpu size')

        else:
            ram_vcpu_size(vimObjectId)

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']
        log.error('Error executing curl command for fetching the project vim object id ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for fetching the vim object id')
        connection.close()
        assert False


def add_default_user_roles(connection, roles='heat_stack_owner,_member_'):
    """
    Add default user roles to the EOCM which is required during project creation.
    Default user roles - heat_stack_owner,_member_ or heat_stack_owner,member depending on the
    role name present in the openstack
    """
    try:
        log.info("Start adding default user roles %s to the EOCM", roles)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_PI.get_core_vm_hostname(Ecm_PI)
        ecm_environment = Ecm_PI.get_ecm_host_name(Ecm_PI)
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

        if is_cloudnative and ecm_environment == 'TEST_HOTEL_QUEENS':
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname, is_ecm=True)
        else:
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        file_name = "userRoleConfig.json"
        log.info("Updating file %s", file_name)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['configdata', 0], 'paramValue', roles)
        sftp = connection.open_sftp()
        log.info("Transferring file %s to %s", file_name, ecm_server_ip)
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()
        command = (f"curl -X POST --insecure --header 'Content-Type: application/json' --header "
                   f"'Accept: application/json' --header 'AuthToken:{token}' --data @{file_name} "
                   f"https://{core_vm_hostname}/ecm_service/configdata")
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('command output %s', command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        request_status = output['status']['reqStatus']

        if 'SUCCESS' in request_status:
            log.info('Adding default user roles %s to the EOCM is successful', roles)
        else:
            log.error('Failed to add default user roles %s to the EOCM', roles)

    except Exception as error:
        log.error("Failed to add default user roles %s to the EOCM: %s", roles, str(error))
        assert False


def verify_project_exists():
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    core_vm_hostname = Ecm_PI.get_core_vm_hostname(Ecm_PI)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    project_name = EPIS.get_project_name(EPIS)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
    is_master_present = check_project_exist(connection, token, core_vm_hostname, project_name)

    try:
        if is_master_present[0]:
            log.info('Project does exist in cCM')
        else:
            log.info('Project does not exist in cCM')

        with open('ccm_master_present.properties', 'w') as f:
            f.write('{0}={1}\n'.format('is_master_present', is_master_present[0]))

    except IOError as error:
        log.error('Project verification failed: %s', str(error))
        assert False

    except Exception as error:
        log.error('Project verification failed: %s', str(error))
        assert False


def project_creation():
    connection = None
    try:
        log.info('start project creation')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_PI.get_core_vm_hostname(Ecm_PI)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        project_name = EPIS.get_project_name(EPIS)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        project_exists = check_project_exist(connection, token, core_vm_hostname, project_name)

        if project_exists[0]:
            log.info('project already exists with name %s', project_name)
            log.info('project Id : %s', project_exists[1])
            log.info('vim object Id  : %s', project_exists[2])
            projectid = project_exists[1]
            vimObjectId = project_exists[2]
            runtime_attr_dict['CEE_TENANT_ID'] = vimObjectId
            runtime_attr_dict['PROJECT_ID'] = projectid
        else:
            log.info('project does not exists with name %s', project_name)
            is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
            file_name = 'createProject.json'

            if is_cloudnative:
                user_roles = get_openstack_user_roles()
                if 'member' in user_roles:
                    add_default_user_roles(connection, 'heat_stack_owner,member')
                    update_create_project_file('member')
                elif '_member_' in user_roles:
                    add_default_user_roles(connection)
                    update_create_project_file('_member_')
                else:
                    log.error("default user role is unknown")
                    assert False
            else:
                update_create_project_file('_member_')

            log.info('vimzone_id from created vimzone : %s', vimzone_id)
            Json_file_handler.modify_second_level_attr(Json_file_handler,
                                                       'com_ericsson_do_auto_integration_files/' + file_name,
                                                       'vimZoneConnections', 0, 'vimZoneId', vimzone_id)
            sftp = connection.open_sftp()
            sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
            sftp.close()
            log.info('creating the project using the token for authentication ')
            command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/projects'''.format(
                token, file_name, core_vm_hostname)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            log.info('Project creation curl output: %s', command_output)
            output = ast.literal_eval(command_output[2:-1:1])
            request_status = output['status']['reqStatus']

            if 'SUCCESS' in request_status:
                order_id = output['data']['order']['id']
                order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                             core_vm_hostname,
                                                                             order_id, 10)
                if order_status:
                    log.info('Order Status is completed %s', order_id)
                    log.info('Created project successfully :  %s', command_output)
                    log.info('order status output: %s', order_output)
                    log.info('Fetching project id from order output ')
                    project_id = order_output['data']['order']['orderItems'][0]['createProject']['id']
                    log.info('project id is: %s', project_id)
                    project_vimObject_Id(connection, core_vm_hostname, project_id, token)
                    log.info('project creation ends')
                else:
                    log.info('order status output: %s', order_output)
                    log.info('Order Status is failed with message mentioned above; %s', order_id)
                    assert False

            elif 'ERROR' in request_status:
                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for creating the project: %s', command_error)
                assert False

    except Exception as error:
        log.error('project creation failed: %s', str(error))
        assert False
    finally:
        if connection:
            connection.close()


def check_vdc_exist(connection, token, core_vm_hostname, vdc_name):
    old_version = '1.11.0-437'
    ecm_verison = get_ccm_version(connection, token, core_vm_hostname, old_version)
    if ecm_verison:
        command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/vdcs'''.format(
            token, core_vm_hostname)
    else:
        command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/v2/vdcs'''.format(
            token, core_vm_hostname)
    log.info('command to get vdc name ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    command_out = ast.literal_eval(command_out)
    requestStatus = command_out['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        if 'data' in command_out:
            output = command_out["data"]["vdcs"]
            for vdc_data in output:
                name = vdc_data['name']
                if vdc_name == name:
                    vdc_id = vdc_data['id']

                    return True, vdc_id

        return False, ''

    elif 'ERROR' in requestStatus:

        command_error = command_out['status']['msgs'][0]['msgText']
        log.error('Error executing curl command for getting the vdc name command :  ' + command_error)
        Report_file.add_line('Error executing curl command for getting the vdc name command :  ')
        Report_file.add_line(command_error)
        connection.close()
        assert False


def vdc_creation():
    log.info('start VDC creation')
    Report_file.add_line('VDC creation begins...')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    epis_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vdc_name = sit_data._SIT__vdc_name
    ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name

    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    log.info('Checking if vdc already exists.')
    Report_file.add_line('Checking if vdc already exists.')
    vdc_exists = check_vdc_exist(connection, token, core_vm_hostname, vdc_name)

    if True == vdc_exists[0]:

        log.info('vdc already exists with name ' + vdc_name)
        Report_file.add_line('vdc already exists with name ' + vdc_name)
        vdc_id = vdc_exists[1]
        epis_host_data._EPIS__vdc_id = vdc_id
        runtime_attr_dict['VDC_ID'] = vdc_id
        log.info('vdc id  ' + vdc_id)
        Report_file.add_line('vdc id : ' + vdc_id)
        connection.close()

        log.info('vdc creation ends.')


    else:

        log.info('waiting 90 seconds till project come up successfully')
        time.sleep(90)

        file_name = r'createvdc.json'
        update_createvdc_file(file_name)

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

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
                log.info('Created VDC successfully using the token for authentication ')
                log.info('Created VDC successfully :  ' + command_output)
                Report_file.add_line('Executed the curl command for VDC creation :  ' + command_output)
                Report_file.add_line('Created VDC successfully')
                log.info(order_output)
                log.info('Fetching VDC ID ')
                Report_file.add_line('Fetching VDC ID')
                vdc_id = order_output['data']['order']['orderItems'][0]['createVdc']['id']
                vdc_name = order_output['data']['order']['orderItems'][0]['createVdc']['name']
                log.info('Fetched VDC ID :' + vdc_id)
                epis_host_data._EPIS__vdc_id = vdc_id
                Report_file.add_line('Executed the curl command for Fetching VDC ID :  ' + command_output)
                Report_file.add_line('Fetched VDC ID :' + vdc_id)

                runtime_attr_dict['VDC_ID'] = vdc_id
                runtime_attr_dict['VDC_NAME'] = vdc_name
                log.info('waiting 120 second to finish vdc creation')
                time.sleep(120)

            else:

                log.info(order_output)
                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the VDC ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for creating the VDC')
            connection.close()
            assert False

        connection.close()
        log.info('VDC creation ends')
        Report_file.add_line('VDC creation ends...')


def check_block_storage_exist(connection, token, core_vm_hostname, name):
    command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/bsvs'''.format(
        token, core_vm_hostname)
    log.info('command to get block storage name : ' + command)
    Report_file.add_line('command to get block storage name : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    command_out = ast.literal_eval(command_out)
    requestStatus = command_out['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        if 'data' in command_out:
            output = command_out["data"]["bsvs"]
            for bs_data in output:
                block_storage_name = bs_data["name"]
                if block_storage_name == name:
                    return True

        return False

    elif 'ERROR' in requestStatus:

        command_error = command_out['status']['msgs'][0]['msgText']
        log.error(
            'Error executing curl command for getting the block storage name command :  ' + command_error)
        Report_file.add_line('Error executing curl command for getting the block storage name command :  ')
        Report_file.add_line(command_error)
        connection.close()
        assert False


def create_genric_block_storage(name, volume, vdc_id):
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    log.info('Checking if block storage already exists.')
    Report_file.add_line('Checking if block storage already exists.')
    bs_exists = check_block_storage_exist(connection, token, core_vm_hostname, name)
    if True == bs_exists:

        log.info('block storage already exists with name : ' + name)
        Report_file.add_line('block storage already exists with name : ' + name)
        connection.close()

    else:
        log.info('block storage does not exists with name ' + name)

        log.info('creating the Block Storage using the token for authentication ')
        Report_file.add_line('Creating Block Storage using the token for authentication ')

        file_name = r'BlockStorage.json'
        update_blockStorage_file(file_name, ecm_environment, name, volume, vdc_id)

        sftp = connection.open_sftp()
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/bsvs'''.format(
            token, file_name, core_vm_hostname)
        command = curl
        Report_file.add_line('Block Storage creation curl ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Block Storage creation curl output  ' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            log.info('Order id for blockStorage creation is ' + order_id)
            Report_file.add_line('Order id for blockStorage creation is ' + order_id)
            log.info(command_output)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname,
                                                                         order_id, 30)

            if order_status:

                log.info('Order Status is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                cinder_id = order_output['data']['order']['orderItems'][0]['createBsv']['id']
                log.info('Block Storage id ' + cinder_id)
                Report_file.add_line('Block Storage id ' + cinder_id)
                log.info('Block Storage Creation ends')
                Report_file.add_line('Block Storage Creation ends')
                connection.close()
                return cinder_id
            else:

                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for blockStorage creation ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for blockStorage creation')
            connection.close()
            assert False


def create_block_storage():
    log.info('start creation block storage')
    Report_file.add_line('Block Storage creation begins...')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    vdc_id = EPIS_data._EPIS__vdc_id
    name = 'Bsv_dummy'
    volume = 1
    cinder_id = create_genric_block_storage(name, volume, vdc_id)


def create_key_pair():
    log.info('start key pair creation')
    Report_file.add_line(' Key pair creation begins...')

    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    epis_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

    tenant_name = epis_host_data._EPIS__tenant_name
    vimzone_name = epis_host_data._EPIS__vimzone_name

    ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    log.info('creating the key pair using the token for authentication ')

    file_name = 'createKey.json'
    key_name = 'key_' + ecm_environment + '_' + str(random.randint(0, 999))
    keypair_data = {"tenantName": tenant_name, "name": key_name}
    Json_file_handler.update_json_file(Json_file_handler,
                                       r'com_ericsson_do_auto_integration_files/' + file_name,
                                       keypair_data)

    sftp = connection.open_sftp()
    sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
    sftp.close()

    curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/securitykeys{}'''.format(
        token, file_name, core_vm_hostname, "'")
    command = curl
    Report_file.add_line('Key Pair creation curl   ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Key pair creation curl output  ' + command_output)
    output = ast.literal_eval(command_output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        key_id = output['data']['securityKey']['id']
        log.info('key name:' + key_name + ' with id ' + key_id)
        Report_file.add_line('key name:' + key_name + 'with id ' + key_id)
        log.info('key created successfully. Ready to transfer  ')
        Report_file.add_line('Executed the curl command for creation of key : ' + key_name + key_id)
        Report_file.add_line('Created key successfully. Ready to transfer')

        file_name = 'transferKey.json'
        key_transfer_data = {"vimZones": [{"name": vimzone_name}]}
        Json_file_handler.update_json_file(Json_file_handler,
                                           r'com_ericsson_do_auto_integration_files/' + file_name,
                                           key_transfer_data)

        sftp = connection.open_sftp()
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/securitykeys/{}/transfer{}'''.format(
            token, file_name, core_vm_hostname, key_id, "'")
        command = curl
        Report_file.add_line('Key Pair transfer curl ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Key pair transfer curl output  ' + command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']
        log.info('Key pair transfer curl output ' + command_output)
        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            log.info('Order id for transferring key is ' + order_id)
            Report_file.add_line('Order id for transferring key is is ' + order_id)
            log.info(command_output)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 10)

            if order_status:

                log.info('Order Status is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info(order_output)

            else:

                log.info(order_output)
                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for transferring the key ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for transferring the key')
            connection.close()
            assert False


    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for creating the key ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for creating the key')
        connection.close()
        assert False

    connection.close()
    log.info('Key pair Creation and transfer ends')
    Report_file.add_line('Key pair Creation and transfer ends')


def icmp_rule():
    try:

        log.info('ICMP Rules ')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType

        if cloud_type == 'OPENSTACK':

            log.info('Cloud Type is  ' + cloud_type + ' Creating the ICMP rules. ')
            Report_file.add_line('Cloud Type is  ' + cloud_type + ' Creating the ICMP rules.')
            openstack_ip = EPIS_data._EPIS__openstack_ip
            username = EPIS_data._EPIS__openstack_username
            password = EPIS_data._EPIS__openstack_password
            openrc_filename = EPIS_data._EPIS__openrc_filename
            project_name = EPIS_data._EPIS__project_name

            ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

            command = 'source {}'.format(openrc_filename)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

            command = 'openstack security group list --project {} | grep default'.format(project_name)
            Report_file.add_line('Security group list ' + command)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            log.info('output of security list command ' + str(stdout))
            security_list = []
            for line in stdout:
                try:
                    security_data = line.split('|')
                    security_list.append(security_data[1].strip())

                except:
                    log.info('')

            log.info(security_list)

            security_id = security_list[0]
            log.info(security_id)

            command = 'openstack security group show {} | grep icmp '.format(security_id)
            Report_file.add_line('Security group list ' + command)
            print(command)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

            if stdout:

                log.info('ICMP Rules are already created ' + str(stdout))
                Report_file.add_line('ICMP Rules are already created ' + str(stdout))

            else:

                log.info('ICMP Rules are now getting created. ')
                Report_file.add_line('ICMP Rules are now getting created. ')
                command = 'openstack security group rule create {} --protocol icmp --ingress --remote-ip 0.0.0.0/0'.format(
                    security_id)
                Report_file.add_line('ingress rule create ' + command)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                time.sleep(2)
                log.info('ingress ICMP Rule created ' + str(stdout))
                Report_file.add_line('ingress ICMP Rule created ' + str(stdout))
                command = 'openstack security group rule create {} --protocol icmp --egress --remote-ip 0.0.0.0/0'.format(
                    security_id)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
                Report_file.add_line('egress rule create ' + command)
                time.sleep(2)
                log.info('egress ICMP Rule created ' + str(stdout))
                Report_file.add_line('egress ICMP Rule created ' + str(stdout))
                log.info('Creation of ICMP Rules finished')
                Report_file.add_line('Creation of ICMP Rules finished')

            ShellHandler.__del__(ShellHandler)


        else:

            log.info('As Cloud Type is  ' + cloud_type + ' ICMP rules creation is not required.')
            Report_file.add_line('As Cloud Type is  ' + cloud_type + ' ICMP rules creation is not required.')


    except Exception as e:

        ShellHandler.__del__(ShellHandler)
        log.info('Error in Creating the ICMP Rules' + str(e))
        Report_file.add_line('Error in Creating the ICMP Rules ' + str(e))
        assert False


def check_network_exist(connection, token, core_vm_hostname, network_name):
    command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/v2/vns'''.format(
        token, core_vm_hostname)
    log.info('command to get network name ' + command)
    Report_file.add_line('command to get network name ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    command_out = ast.literal_eval(command_out)
    requestStatus = command_out['status']['reqStatus']
    if 'SUCCESS' in requestStatus:
        if 'data' in command_out:
            output = command_out["data"]["vns"]
            for network_data in output:
                name = network_data["name"]
                log.info('net name ' + name)
                if network_name == name:
                    vimObjectId_id = network_data['vimObjectId']
                    return True, vimObjectId_id

        return False, ''

    elif 'ERROR' in requestStatus:

        command_error = command_out['status']['msgs'][0]['msgText']
        log.error('Error executing curl command for getting the network name command :  ' + command_error)
        Report_file.add_line('Error executing curl command for getting the network name command :  ')
        Report_file.add_line(command_error)
        connection.close()
        assert False


def update_internal_network_vimObject_id(connection, token, core_vm_hostname, virtual_net_id):
    log.info('start fetching vim object id for internal network')
    curl = '''curl --insecure 'https://{}/ecm_service/v2/vns/{}' -H 'AuthToken:{}' -H 'Accept: application/json{}'''.format(
        core_vm_hostname, virtual_net_id, token, "'")
    Report_file.add_line('internal Network: Fetch vim object id curl ' + curl)

    command_output = ExecuteCurlCommand.get_json_output(connection, curl)
    Report_file.add_line('internal Network: Fetch vim object id curl output ' + command_output)

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        internal_network_vimObject_id = output['data']['vn']['vimObjectId']
        log.info('vim_object_id is ' + internal_network_vimObject_id)
        Report_file.add_line('vim_object_id is ' + internal_network_vimObject_id)


    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for internal network_vimObject_id ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for internal network_vimObject_id')


def create_internal_network():
    log.info('Internal Network creation begins')
    Report_file.add_line('Internal Network creation begins')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    network_name = 'Dualstack_Internal_Network_' + ecm_environment

    network_exists = check_network_exist(connection, token, core_vm_hostname, network_name)

    if True == network_exists[0]:
        vim_object_id = network_exists[1]
        log.info('Internal Network already exists with name : ' + network_name)
        Report_file.add_line('Internal Network already exists with name :' + network_name)
        log.info('vim object id : ' + vim_object_id)
        Report_file.add_line('vim object id : ' + vim_object_id)
        runtime_attr_dict['EXTERNAL_NET_ID'] = vim_object_id
        connection.close()

    else:
        log.info('InternaL Network does not exists with name : ' + network_name)
        Report_file.add_line('InternaL Network does not exists with name : ' + network_name)
        file_name = 'internalNetwork.json'

        update_internal_network_creation_file(file_name)

        sftp = connection.open_sftp()
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('creating the internal network using the token for authentication ')
        Report_file.add_line('creating the internal network using token for authentication  ')

        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/v2/vns'''.format(
            token, file_name, core_vm_hostname)
        command = curl
        Report_file.add_line('Internal Network creation curl ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Internal Network curl output ' + command_output)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            log.info('Order id for internal network creation  ' + order_id)
            Report_file.add_line('Order id for internal network creation  ' + order_id)
            log.info(command_output)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 10)

            if order_status:

                log.info('Order Status is completed ' + order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info('Created internal network successfully :  ' + command_output)
                Report_file.add_line('Created internal network successfully' + command_output)
                virtual_net_id = order_output['data']['order']['orderItems'][0]['createVn']['id']
                log.info('wait 5 seconds to complete the internal network vimobject id ')
                time.sleep(5)
                update_internal_network_vimObject_id(connection, token, core_vm_hostname, virtual_net_id)


            else:

                log.info('Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for internal network creation ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for creating the internal network')
            connection.close()
            assert False

        connection.close()
        log.info('internal network creation ends')
        Report_file.add_line('internal network creation ends...')


def update_network_vimObject_id(connection, token, core_vm_hostname, external_network_id):
    log.info('start fetching vim object id for network')
    curl = '''curl --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/v2/vns/{}{}'''.format(
        token, core_vm_hostname, external_network_id, "'")
    Report_file.add_line('External Network: Command to fetch vim object id  ' + curl)

    command_output = ExecuteCurlCommand.get_json_output(connection, curl)
    Report_file.add_line('External Network: Command output to fetch vim object id  ' + command_output)

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        vim_object_id = output['data']['vn']['vimObjectId']
        log.info('vim_object_id is ' + vim_object_id)
        Report_file.add_line('vim_object_id is ' + vim_object_id)

        runtime_attr_dict['EXTERNAL_NET_ID'] = vim_object_id
        log.info('putting run time file on blade with updated values')
        put_runtime_env_file_attr_dict()

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for network_vimObject_id ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for network_vimObject_id')


def create_external_network():
    log.info('start external network creation')
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    core_vm_hostname = Ecm_PI.get_core_vm_hostname(Ecm_PI)
    ecm_environment = Ecm_PI.get_ecm_host_name(Ecm_PI)
    cloud_type = EPIS.get_cloud_manager_type(EPIS)
    vim_type = EPIS.get_static_project(EPIS)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
    network_details = get_network_details(cloud_type, ecm_environment)

    network_name = network_details[0]

    log.info('checking whether external network already exits with name %s or not.'.format(network_name))
    network_exists = check_network_exist(connection, token, core_vm_hostname, network_name)

    if True == network_exists[0]:

        log.info('External network already exists with name: %s ', network_name)
        vim_object_id = network_exists[1]
        log.info('vim object id: %s', vim_object_id)
        runtime_attr_dict['EXTERNAL_NET_ID'] = vim_object_id
        connection.close()

    else:
        if vim_type == 'ORCH_STAGING_N53':
            log.info('Checking if network exist in openstack')
            external_network_name = check_existing_external_network()
            if external_network_name == network_name:
                log.info('External network present in openstack, needs to be deleted')
                delete_external_network_CEE(network_name)
        else:
            log.info('External network does not exists with name ' + network_name)

        file_name = 'providerNetwork.json'

        update_external_network_creation_file(file_name)

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        log.info('creating the external network using the token for authentication ')

        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/v2/vns'''.format(
            token, file_name, core_vm_hostname)
        command = curl

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('External network Creation curl output: %s ', command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            log.info('Order id for external network creation: %s', order_id)
            log.info(command_output)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 10)

            if order_status:

                log.info('Order Status is completed: %s', order_id)
                log.info('Created external network successfully : %s', command_output)
                external_network_id = order_output['data']['order']['orderItems'][0]['createVn']['id']
                log.info('External network id: %s', external_network_id)
                log.info('wait 5 seconds to complete the vimobject id ')
                time.sleep(5)
                update_network_vimObject_id(connection, token, core_vm_hostname, external_network_id)

            else:

                log.info('Order Status is failed with message mentioned above: %s', order_id)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for creating the external network: %s', command_error)
            connection.close()
            assert False

        connection.close()
        log.info('external network creation ends')


def create_bgw_ports():
    log.info('start BGW ports creation')
    Report_file.add_line(' BGW ports creation begins...')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cloud_type = EPIS_data._EPIS__cloudManagerType

    if cloud_type == 'CEE':
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        gatway_ip = EPIS_data._EPIS__network_gatway_ip
        openrc_filename = EPIS_data._EPIS__openrc_filename

        ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        network_name = 'P3_' + cloud_type + '01_' + ecm_environment + '_PROV'
        ipv4_network_name = 'P3_' + ecm_environment + '_IPv4'

        # fetch the available IP for port creation

        command = 'openstack port list --network {} | grep -i ACTIVE '.format(network_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        existing_ips = []
        for line in stdout:
            port_data = line.split('|')
            fixed_ip_address = port_data[4].strip()
            ip_data = fixed_ip_address.split(',')
            ip_address = ip_data[0].strip()
            ip_num = ip_address.split('=')
            ip = ip_num[1].strip()
            existing_ips.append(ip[1:-1:])

        avail_ip_list = []
        i = 1
        while avail_ip_list.__len__() != 2:
            ip_add = str(ipaddress.ip_address(gatway_ip) + i)

            if ip_add in existing_ips:
                log.info(
                    'IP {} for bgw port create already exists , searching for new IP address '.format(ip_add))
            else:
                log.info('IP {} is available for bgw port creation  '.format(ip_add))
                avail_ip_list.append(ip_add)

            i = i + 1

        for i in range(1, 3):
            port_name = network_name + '_bgw_' + str(i)
            ip_add = avail_ip_list[i - 1]
            command = 'neutron port-create --name {} --fixed-ip subnet_id={},ip_address={} --device_owner=baremetal:BGW-{} --binding:host_id=BGW-{} {}'.format(
                port_name, ipv4_network_name, ip_add, i, i, network_name)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        log.info(' BGW ports creation ends')
        Report_file.add_line('BGW ports creation ends...')

    else:

        log.info(' BGW ports creation not required for cloud type : ' + cloud_type)
        Report_file.add_line(' BGW ports creation not required for cloud type : ' + cloud_type)


def create_flavour(flavor_file, flavor_transfer_file, flavor_name):
    try:
        log.info('start flavour creation ' + flavor_name)
        Report_file.add_line('flavour creation begins... ' + flavor_name)

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        # done for ticket SM-102100
        file_number = str(random.randint(1, 999))
        put_flavor_file = f"flavour_{file_number}.json"
        put_flavor_transfer_file = f"flavour_transfer_{file_number}.json"

        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        log.info('creating the flavour using the token for authentication ')

        ServerConnection.put_file_sftp(connection,
                                       r'com_ericsson_do_auto_integration_files/' + flavor_file,
                                       SIT.get_base_folder(SIT)+put_flavor_file)

        log.info('Start creating curl command for flavour creation ')

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/srts{}'''.format(
            token, put_flavor_file, core_vm_hostname, "'")

        Report_file.add_line('Executing curl command for flavour creation ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        Report_file.add_line('Flavour creation curl output  ' + command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            flavour_id = output['data']['srt']['id']
            log.info('Flavour created successfully with id : %s', flavour_id)
            Report_file.add_line('Flavour created successfully with id :' + flavour_id)



        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for creating the flavour %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for creating the flavour')
            assert False

        ServerConnection.put_file_sftp(connection,
                                       r'com_ericsson_do_auto_integration_files/' + flavor_transfer_file,
                                       SIT.get_base_folder(SIT)+put_flavor_transfer_file)

        log.info('Start creating curl command for flavour transfer to VIM ')
        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/srts/{}/transfer{}'''.format(
            token, put_flavor_transfer_file, core_vm_hostname, flavour_id, "'")

        Report_file.add_line('Flavour transfer curl  ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Flavour transfer curl output ' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname,
                                                                         order_id, 10)
            if order_status:
                log.info('Order Status is completed %s', order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info('Flavour transfered to VIM  successfully with order id  : %s', order_id)
                Report_file.add_line('Flavour transfered to VIM  successfully with order id  :' + order_id)


            else:
                log.info(order_output)
                log.info('Order Status is failed with message mentioned above %s', order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                assert False




        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for transferring the flavour to vim %s ', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for transferring the flavour to vim')
            assert False

        log.info('End flavour creation')
        Report_file.add_line('flavour creation Ends...')

    except Exception as e:
        log.error('Error while create-transfer flavor in EOCM  %s ', str(e))
        Report_file.add_line('Error while create-transfer flavor in EOCM ' + str(e))
        assert False

    finally:
        log.info('Going to remove the flavor files used from server')
        command = f"rm -rf {put_flavor_file} {put_flavor_transfer_file}"

        Report_file.add_line('command  ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Command output ' + command_output)
        log.info('files removed from server')
        connection.close()


def image_registration(file_name):
    log.info('start Image registration ')
    Report_file.add_line('Image registration begins... ')

    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    log.info('Generating token in the host blade server using the  curl command  ')
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
    log.info('Registering the Image using the token for authentication ')

    Report_file.add_line('Registering the Image using the token for authentication ')
    ServerConnection.put_file_sftp(connection,
                                   r'com_ericsson_do_auto_integration_files/' + file_name,
                                   SIT.get_base_folder(SIT) + file_name)

    curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/images/register'''.format(
        token, file_name, core_vm_hostname)
    command = curl
    Report_file.add_line('Image Registration curl ' + command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Image Registration curl output ' + command_output)

    output = ast.literal_eval(command_output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        msg_text = output['status']['msgs'][0]['msgText']
        vimImageObjectId = output['status']['msgs'][0]['msgValues'][0]
        log.info(msg_text + vimImageObjectId)
        Report_file.add_line(msg_text + vimImageObjectId)
        log.info('VIM image object ID registered')
        log.info(command_output)
        Report_file.add_line('Executed the curl command for image registration : ' + command_output)
        Report_file.add_line('VIM image object ID registered')

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for registering the image ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for registering the image')
        connection.close()
        assert False

    connection.close()
    log.info('Image registration ends')
    Report_file.add_line('image registration ends')


def run_invoke_command_certs(connection, command, password):
    log.info(command)

    interact = connection.invoke_shell()

    interact.send(command + '\n')
    time.sleep(5)
    resp = interact.recv(9999)
    buff = str(resp)
    log.info(buff)
    if 'continue connecting' in buff:
        interact.send('yes\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)

    if 'password' in buff:
        interact.send(password + '\n')

    time.sleep(5)
    interact.shutdown(2)


def queens_certs_key():
    try:

        log.info('Start Applying Queens Cert and Key begin')
        Report_file.add_line('Start Applying Queens Cert and Key begin')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        username = core_vm_data._Ecm_PI__CORE_VM_USERNAME
        password = core_vm_data._Ecm_PI__CORE_VM_PASSWORD
        deployment_type = core_vm_data._Ecm_PI__deployment_type
        cloud_type = EPIS_data._EPIS__cloudManagerType
        vim_name = EPIS_data._EPIS__vimzone_name
        ecm_server_ip = core_vm_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = core_vm_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = core_vm_data._Ecm_PI__ECM_Host_Blade_Password

        if deployment_type == 'HA':
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP

        if cloud_type == 'OPENSTACK':

            if vim_name == 'cloud7a_ORCH_Staging_C7a_dynamic' or vim_name == 'testHotel_Queens':

                cert_path = '/var/tmp/QUEENS_CERT/' + vim_name
                key_file = 'ecm_ssl.key'
                cert_file = 'ecm_ssl.crt'
                cert_file_path = cert_path + '/' + cert_file
                key_file_path = cert_path + '/' + key_file
                connection = ServerConnection.get_connection(ecm_server_ip, ecm_username,
                                                             ecm_password)

                # command to clear the ip from ssh_host file
                remove_ip = 'ssh-keygen -R {}'.format(core_vm_ip)
                connection.exec_command(remove_ip)

                source_certs_path = cert_file_path
                destination_certs_path = "/etc/pki/tls/certs/" + cert_file
                log.info('Copying ' + source_certs_path + ' to - ' + core_vm_ip)
                Report_file.add_line('Copying ' + source_certs_path + ' to - ' + core_vm_ip)
                ServerConnection.transfer_files_with_user_and_passwd(connection, username, password,
                                                                     source_certs_path, core_vm_ip,
                                                                     destination_certs_path)
                log.info('Transferring of ' + source_certs_path + ' file has been completed')
                Report_file.add_line('Transferring of ' + source_certs_path + ' file has been completed')

                source_filepath = key_file_path
                destination_filepath = '/etc/pki/tls/private/' + key_file
                log.info('Copying ' + source_certs_path + ' to - ' + core_vm_ip)
                Report_file.add_line('Copying ' + source_certs_path + ' to - ' + core_vm_ip)
                ServerConnection.transfer_files_with_user_and_passwd(connection, username, password,
                                                                     source_filepath, core_vm_ip,
                                                                     destination_filepath)
                log.info('Transferring of ' + source_filepath + ' file has been completed')
                Report_file.add_line('Transferring of ' + source_filepath + ' file has been completed')
                connection.close()

                connection = ServerConnection.get_connection(core_vm_ip, username, password)

                command = 'systemctl restart httpd'
                stdin, stdout, stderr = connection.exec_command(command)

                log.info('Finished Applying Queens Cert and Key ')
                Report_file.add_line('Finished Applying Queens Cert and Key ')
                connection.close()

            else:

                log.info('No need to apply certs and key file for this vim name ' + vim_name)
                Report_file.add_line('No need to apply certs and key file for this vim name ' + vim_name)


        else:

            log.info('No need to apply certs and key file for this cloud type ' + cloud_type)
            Report_file.add_line('No need to apply certs and key file for this cloud type ' + cloud_type)



    except Exception as e:

        log.info('Error Applying Queens Cert and Key begin ' + str(e))
        Report_file.add_line('Error Applying Queens Cert and Key begin ' + str(e))
        assert False


def eocm_ha_certificates():
    try:
        platform = Server_details.get_environment_user_platform(Server_details)

        log.info(f'Start to install EO_CM certificate in {platform} platform ')

        abcd_vm_serverip, abcd_username, abcd_password = Server_details.get_abcd_vm_details(Server_details)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        deployment_type = Server_details.get_deployment_type(Server_details)
        abcd_connection = None

        if 'HA' == deployment_type:
            abcd_connection = ServerConnection.get_connection(abcd_vm_serverip, abcd_username,
                                                              abcd_password)
            log.info('Going to remove existing ecmssl files')

            command = f'rm -rf /ecm-umi/install/{platform}/stage/cert/ecmssl.*'

            log.info('command : %s', command)

            stdin, stdout, stderr = abcd_connection.exec_command(command)

            command_output = str(stdout.read())
            log.info('command output : %s', command_output)

            abcd_connection.close()

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            log.info('Going to transfer certificate and key files from blade to ABCD VM ')

            source_path = '/var/tmp/EO_CM_CERTIFICATES/ecmssl.crt'
            destination_path = f'/ecm-umi/install/{platform}/stage/cert/ecmssl.crt'
            ServerConnection.transfer_files_with_user_and_passwd(connection, abcd_username,
                                                                 abcd_password, source_path, abcd_vm_serverip,
                                                                 destination_path)

            source_path = '/var/tmp/EO_CM_CERTIFICATES/ecmssl.key'
            destination_path = f'/ecm-umi/install/{platform}/stage/cert/ecmssl.key'
            ServerConnection.transfer_files_with_user_and_passwd(connection, abcd_username,
                                                                 abcd_password, source_path, abcd_vm_serverip,
                                                                 destination_path)

            log.info('Finished to transfer certificate and key files from blade to ABCD VM ')
            connection.close()
            time.sleep(2)
            log.info('Going to set SSL_ONLY = true ')
            abcd_connection = ServerConnection.get_connection(abcd_vm_serverip, abcd_username,
                                                              abcd_password)

            command = f"sed -i 's/SSL_ONLY=false/SSL_ONLY=true/g' /ecm-umi/install/{platform}/.baseenv.HA.int"

            log.info('command : %s', command)

            stdin, stdout, stderr = abcd_connection.exec_command(command)

            command_output = str(stdout.read())
            print('error output' + str(stderr.read()))
            log.info('command output : %s', command_output)
            time.sleep(5)

            log.info('Going to trigger install script with multiple arguments ')

            if 'kvm' == platform:
                script_arguments = ['anp3', 'anp6', 'anp7', 'anp10']
            elif 'eoo' == platform:
                script_arguments = ['anp4a', 'anp4d', 'anp4e', 'anp4ga']
            else:
                log.error(
                    f'Wrong platform input on DIT attibute name is ENVIRONMENT_USER_PLATFORM and value given is {platform}')
                assert False

            for argument in script_arguments:
                command = f"cd /ecm-umi/install/{platform} ; ./ecmInstall_HA.sh -{argument}"

                log.info(command)

                log.info('Please wait for command to execute ....')

                stdin, stdout, stderr = abcd_connection.exec_command(command)

                command_output = str(stdout.read())

                log.info('command output : %s', command_output)
                if 'failed=[1-9][0-9]?[0-9]?' in command_output:
                    log.error('Error occured , please check the report file for command output ')
                    assert False

            log.info('Going to set SSL_ONLY = false ')
            time.sleep(2)
            command = f"sed -i 's/SSL_ONLY=true/SSL_ONLY=false/g' /ecm-umi/install/{platform}/.baseenv.HA.int"

            log.info('command : %s', command)

            stdin, stdout, stderr = abcd_connection.exec_command(command)

            command_output = str(stdout.read())
            log.info('command output : %s', command_output)
            time.sleep(2)
            log.info('Finished to install EO_CM certificate in %s platform ', platform)
        elif 'NON-HA' == deployment_type and 'kvm' == platform or 'eoo' == platform:
            log.info('Deployment type is %s and platform is %s', deployment_type, platform)
            queens_certs_key()
        else:
            log.info('Deployment type is %s and platform is %s', deployment_type, platform)
            log.info('No Certificates would be installed in this scenario \n **** UNDER THOUGHT PROCESS **** ')



    except Exception as e:
        log.error(f'Failed to install EO_CM certificate in %s platform , ERROR: %s', platform, str(e))
        assert False
    finally:
        if abcd_connection:
            abcd_connection.close()


def renew_eocm_certs():
    connection = None
    try:
        log.info('Start taking backup of key and certificate from existing secret')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
        eocm_namespace = Ecm_core.get_ecm_namespace(Ecm_core)
        ecm_certificate_path = Ecm_core.get_ecm_certificate_path(Ecm_core)
        ecm_certificate_bkp_path = Ecm_core.get_ecm_certificate_bkp_path(Ecm_core)
        ecm_fqdn = Ecm_core.get_core_vm_hostname(Ecm_core)

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        log.info(' taking backup of certificate and key file ')

        connection = get_VMVNFM_host_connection()

        command_crt_bkp = '''kubectl get secret eric-eo-cm-nbi-tls-cert -n {} -o jsonpath="{{.data['tls\.crt']}}" | base64 -d > {}/certificate_file_backup.crt'''.format(
            eocm_namespace, ecm_certificate_bkp_path)
        command_key_bkp = '''kubectl get secret  eric-eo-cm-nbi-tls-cert -n {} -o jsonpath="{{.data['tls\.key']}}" | base64 -d > {}/key_file_backup.key'''.format(
            eocm_namespace, ecm_certificate_bkp_path)

        log.info('command to take backup of certificate: %s', command_crt_bkp)

        log.info('command to take backup of key: %s', command_key_bkp)

        stdin, stdout, stderr = connection.exec_command(command_crt_bkp, get_pty=True)
        command_output = str(stdout.read())

        log.info('certificate backup command output : %s', command_output)

        stdin, stdout, stderr = connection.exec_command(command_key_bkp, get_pty=True)
        command_output = str(stdout.read())

        log.info('key backup command output : %s', command_output)

        log.info('Deleting already existing secret')

        command_del_secret = 'kubectl delete secret eric-eo-cm-nbi-tls-cert -n {}'.format(eocm_namespace)

        log.info('Command to delete the secret: %s', command_del_secret)

        stdin, stdout, stderr = connection.exec_command(command_del_secret, get_pty=True)
        command_output = str(stdout.read())

        log.info('command output: %s', command_output)

        if '"eric-eo-cm-nbi-tls-cert" deleted' in command_output:
            log.info('secret deleted successfully')

        else:
            log.error('error occured while deleting certificate')
            assert False

        log.info('Recreating secret with %s.key and %s.crt', ecm_fqdn, ecm_fqdn)

        command = f"kubectl create secret tls eric-eo-cm-nbi-tls-cert -n {eocm_namespace} --key {ecm_certificate_path}/{ecm_fqdn}.key --cert {ecm_certificate_path}/{ecm_fqdn}.crt"

        log.info('Command to create secret: %s', command)

        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        command_output = str(stdout.read())

        log.info('command output : ' + command_output)

        if 'secret/eric-eo-cm-nbi-tls-cert created' in command_output:

            log.info('secret created successfully and certificate has been renewed')

        else:
            log.info('secret creation failed')
            assert False

    except Exception as e:

        log.error('Error occured in recreating the secret with exception: %s', str(e))
        assert False

    finally:
        connection.close()


def fetch_existing_external_network_id():
    try:

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        external_network_name = EPIS_data._EPIS__external_network_name
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        ecm_environment = ecm_host_data._Ecm_PI__ECM_Host_Name
        openrc_filename = 'openrcauto_' + ecm_environment

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

        command = 'dos2unix {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'openstack network show {} | grep -w id'.format(external_network_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info(stdout)
        network_data = stdout[0].split('|')
        external_network_id = network_data[2].strip()

        runtime_attr_dict['EXTERNAL_NET_ID'] = external_network_id

    except Exception as e:
        log.error(f'Failed to fetch external network id, ERROR: ' + str(e))
        Report_file.add_line(f'Failed to external network id , ERROR: ' + str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def put_runtime_env_file_attr_dict():
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    enviornment = ecm_host_data._Ecm_core__enviornment
    data_file = r'com_ericsson_do_auto_integration_files/run_time_' + enviornment + '.json'
    dest = r'/root/' + 'run_time_' + enviornment + '.json'
    runtime_file_connection = ServerConnection.get_connection(server_ip, username, password)
    ServerConnection.get_file_sftp(runtime_file_connection, dest, data_file)

    for attribute in runtime_attr_dict.keys():
        value = runtime_attr_dict[attribute]
        log.info(f' Updating run time file attribute {attribute} with value {value}')
        Json_file_handler.modify_attribute(Json_file_handler, data_file, attribute, value)

    ServerConnection.put_file_sftp(runtime_file_connection, data_file, dest)
    runtime_file_connection.close()


def get_eocmversion(connection, token, core_vm_host, old_version):
    try:
        log.info('Start to fetch ECM Version')
        command = '''curl --insecure "https://{}/ecm_service/product" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
            core_vm_host, token)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']
        if 'SUCCESS' in requestStatus:
            current_ecmversion = output['data']['productVersion']['product'][0]['version']
            log.info("Current version of ECM : %s", current_ecmversion)
            if version.parse(current_ecmversion) >= version.parse(old_version):
                log.info('Its Latest ECM Version %s', current_ecmversion)
                return True
            else:
                log.info('Its Latest ECM Version %s', old_version)
                return False
        else:
            log.info('Error while fetching ecm version')
            assert False
    except Exception as error:
        log.error('Error while fetching ecm version %s', error)


def check_existing_external_network():
    try:

        external_network_name = EPIS.get_external_network_name(EPIS)
        openstack_ip, username, password, openrc_filename = Server_details.openstack_host_server_details(Server_details)
        ecm_environment = Ecm_PI.get_ecm_host_name(Ecm_PI)
        openrc_filename = 'openrcauto_' + ecm_environment

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

        command = 'dos2unix {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info(stdout)
        log.error(stderr)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info(stdout)
        log.error(stderr)

        command = 'openstack network show {} | grep -w name'.format(external_network_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info(stdout)
        if stdout:
            network_data = stdout[0].split('|')
            external_network_name = network_data[2].strip()
            log.info(external_network_name)
            return external_network_name
        return stdout

    except Exception as e:
        log.error('Failed to check external network in openstack, ERROR: %s', str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def delete_external_network_CEE(network_name):
    try:

        log.info('Start deleting network from openstack')
        openstack_ip, username, password, openrc_filename = Server_details.openstack_host_server_details(Server_details)
        ecm_environment = Ecm_PI.get_ecm_host_name(Ecm_PI)
        openrc_filename = 'openrcauto_' + ecm_environment
        ipv4_range = EPIS.get_network_ipv4_range(EPIS)
        ip_init = ipv4_range[:-5]

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)

        command = 'dos2unix {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info(stdout)
        log.error(stderr)

        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        log.info(stdout)
        log.error(stderr)

        command = 'openstack port list |grep  {} '.format(ip_init)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(10)
        log.info(stdout)
        log.info('Deleting ports associted with external network')
        ports_to_delete = []
        for line in stdout:
            id = line.split('|')
            port_id = id[1].strip()
            log.info(port_id)
            ports_to_delete.append(port_id)
        log.info(f'All ports associated with external network: {ports_to_delete}')
        for ports in ports_to_delete:
            command = 'openstack port delete {}'.format(ports)
            log.info('command to delete ports associated with network: %s', command)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            time.sleep(5)
            log.info(stdout)
            log.error(stderr)
        log.info('Now deleting the External network')
        command = 'openstack network delete {}'.format(network_name)
        log.info('Command to delete external network: %s', command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        time.sleep(10)
        log.info(stdout)
        log.error(stderr)
        if not stdout:
            log.info('Network has been succesfully deleted')

    except Exception as e:
        log.error('Failed to delete external network from openstack, ERROR: %s', str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)


def get_ccm_version(connection, token, core_vm_host, old_version):
    try:
        log.info('Start to fetch ECM Version')
        command = '''curl --insecure "https://{}/ecm_service/product" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
            core_vm_host, token)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']
        if 'SUCCESS' in requestStatus:
            current_ecmversion = output['data']['productVersion']['product'][0]['version']
            log.info("Current version of ECM : %s", current_ecmversion)
            if version.parse(current_ecmversion) >= version.parse(old_version):
                log.info('Its Latest ECM Version %s', current_ecmversion)
                return True
            else:
                log.info('Its Latest ECM Version %s', old_version)
                return False
        else:
            log.info('Error while fetching ecm version')
            assert False
    except Exception as error:
        log.error('Error while fetching ecm version %s', error)
