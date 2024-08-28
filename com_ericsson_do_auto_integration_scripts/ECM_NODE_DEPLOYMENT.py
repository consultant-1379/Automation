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
# pylint: disable=C0302,C0103,C0114,C0116,W0703,W0212,R1705,R0914,W0612,R1702,R0912,R0915
# pylint: disable=C0209, C0301

import ast
import re
import time
from vnfci_common import misc
from packaging import version

from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_nsd_create_package_file,
                                                                         update_ns_create_package_file,
                                                                         update_runtime_env_file)
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.MYSQL_DB import (
    get_PSQL_connection, get_record_id_from_PSQL_table)
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import (
    delete_tosca_vnf_package, remove_ecm_package_if_exists)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DELETION import get_vapp_list_from_eocm
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import (
    chown_and_file_permission, get_VMVNFM_host_connection, get_vmvnfm_pod, get_vmvnfm_pod_cmd,
    transfer_director_file_to_vm_vnfm,
    get_file_name_from_vm_vnfm,
    get_file_name_from_director_server, get_master_vnflcm_db_pod, fetch_vmvnfm_version)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DELETION import change_db_passwd_when_permission_denied
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities

log = Logger.get_logger('ECM_NODE_DEPLOYMENT.py')


def get_node_vnf_vapp_id_ECM(vapp_name):
    # Vapp_id = id of Vapp on ECM
    # vnfid = id of vapp on VNF-LCM
    try:
        log.info('Start fetching out the vnfid and vapp id for vapp name : %s', vapp_name)
        Report_file.add_line('Start fetching out the vnfid and vapp id for vapp name : ' + vapp_name)
        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        blade_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        auth_token = Common_utilities.authToken(Common_utilities, blade_connection, core_vm_hostname)

        vapp_data = get_vapp_list_from_eocm(blade_connection, auth_token, core_vm_hostname, vapp_name)

        if vapp_data:

            log.info(' Got the data from ECM , fetching out the ids ')

            vapp_id = vapp_data[0]['id']
            vnf_id = vapp_data[0]['managementSystemId']

            log.info('Vapp id : %s', vapp_id)
            log.info('vnf id : %s', vnf_id)

            return vapp_id, vnf_id

        else:
            log.error('No Vapp found , please check in EO-CM for Vapp %s', vapp_name)
            assert False

    except Exception as error:
        log.error('Error fetching out the vnfid and vapp id %s', str(error))
        Report_file.add_line('Error fetching out the vnfid and vapp id ' + str(error))

        assert False
    finally:
        blade_connection.close()


def modify_configurable_node_parameters(node_name, param_name, file_name, vapp_id):
    try:
        log.info(

            'Start modifing configurable parameter * %s * for Vnf_type * %s *',
            param_name,
            node_name
        )
        Report_file.add_line(
            f'Start modifing configurable parameter * {param_name}' +
            ' * for Vnf_type * {node_name} *'

        )

        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        blade_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        auth_token = Common_utilities.authToken(Common_utilities, blade_connection, core_vm_hostname)

        ServerConnection.put_file_sftp(
            blade_connection,
            r'com_ericsson_do_auto_integration_files/' + file_name,
            SIT.get_base_folder(SIT) + file_name,
        )

        command = '''curl --insecure 'https://{}/ecm_service/vapps/{}' -X PATCH -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'AuthToken: {}' --data @{}'''.format(
            core_vm_hostname, vapp_id, auth_token, file_name
        )

        Report_file.add_line('curl command  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(blade_connection, command)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            log.info('order id  : %s', order_id)
            Report_file.add_line('order id  : ' + order_id)
            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities,
                blade_connection,
                auth_token,
                core_vm_hostname,
                order_id,
                20,
            )

            if order_status:
                log.info('Order status is Completed')
                Report_file.add_line('Order status is Completed')
                log.info('Finished modifing configurable parameter * %s * for Vnf_type * %s *',
                         param_name, node_name)
                Report_file.add_line('Finished modifing configurable parameter * {} * for Vnf_type * {} *'.format(
                    param_name, node_name))

            else:
                log.error('Order status is Failed ')
                assert False

    except Exception as error:
        log.error('Error modifing configurable parameter %s', str(error))
        Report_file.add_line('Error modifing configurable parameter ' + str(error))

        assert False
    finally:
        blade_connection.close()


def check_image_registered(connection, image_name, token, core_vm_hostname, transfered_to_vim=False):
    curl = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/images'''.format(
        token, core_vm_hostname
    )

    command = curl
    Report_file.add_line('Executing the curl command for checking image registered ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:

        if 'data' in output:
            image_list = output['data']['images']
            for image_data in image_list:
                name = image_data['name']
                if image_name == name:
                    log.info('Image with name %s already registered', image_name)
                    global image_id
                    image_id = image_data['id']

                    if transfered_to_vim:
                        global vimImageObjectId
                        vimImageObjectId = image_data['vimImages'][0]['vimImageObjectId']
                    return True

            return False
        else:
            log.info('There is no data in check image registered output. ')
            return False

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for checking image registered  %s', command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for checking image registered ')
        connection.close()
        assert False


def get_image_vimobjectId():
    return vimImageObjectId


def remove_host_lcm_entry():
    try:
        log.info('remove old LCM entry from known_hosts file on Host server')
        Report_file.add_line('remove old LCM entry from known_hosts file on Host server')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.get_file_sftp(connection, '/root/.ssh/known_hosts', 'ecm_known_hosts')

        known_hosts = open('ecm_known_hosts', 'r')
        hostlist = known_hosts.readlines()
        known_hosts.close()

        known_hosts = open('ecm_known_hosts_updated', 'w+')
        for line in hostlist:

            if lcm_server_ip in line:
                log.info('removing %s LCM entry from known_hosts file on Host server ', lcm_server_ip)
            else:
                known_hosts.write(line)

        known_hosts.close()
        ServerConnection.put_file_sftp(connection, 'ecm_known_hosts_updated', '/root/.ssh/known_hosts')
        log.info('/root/.ssh/known_hosts updated')
        Report_file.add_line('/root/.ssh/known_hosts updated')
        connection.close()
    except Exception as error:
        log.error('Error remove old LCM entry from known_hosts file on Host server %s', str(error))
        Report_file.add_line('Error remove old LCM entry from known_hosts file on Host server ' + str(error))
        assert False


def update_admin_heatstack_rights():
    try:

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        cloud_type = EPIS_data._EPIS__cloudManagerType

        if cloud_type == 'OPENSTACK':

            log.info('Giving admin and heatstack owner privileges to project_user %s', cloud_type)
            Report_file.add_line('Giving admin and heatstack owner privileges to project_user ' + cloud_type)

            project_name = EPIS_data._EPIS__project_name
            openstack_ip = EPIS_data._EPIS__openstack_ip
            username = EPIS_data._EPIS__openstack_username
            password = EPIS_data._EPIS__openstack_password
            openrc_filename = EPIS_data._EPIS__openrc_filename

            ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
            command = 'source {}'.format(openrc_filename)
            log.info(command)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            command = 'openstack user list | grep -i {}'.format(project_name)
            log.info(command)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

            if stdout:

                command = 'openstack role add --user {}_user --project {} admin ; openstack role add --user {}_user --project {} heat_stack_owner'.format(
                    project_name, project_name, project_name, project_name
                )
                log.info(command)
                stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

                log.info('Admin and Heatstack owner privileges to project_user')
                Report_file.add_line('Admin and Heatstack owner privileges to project_user')

            else:
                log.info('user does not exists')
                Report_file.add_line('user does not exists')
                ShellHandler.__del__(ShellHandler)
                assert False

            ShellHandler.__del__(ShellHandler)

        else:

            log.info(
                'Cloud Type is %s ,admin and heatstack owner privileges not needed ',
                cloud_type
            )

    except Exception as error:
        log.error('Error admin and heatstack owner privileges to project_user %s', str(error))
        Report_file.add_line('Error admin and heatstack owner privileges to project_user ' + str(error))

        assert False


def update_lcm_oss_password():
    try:
        log.info('Start updating vnflcm oss password ')
        Report_file.add_line('Start updating vnflcm oss password ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        new_password = enm_data._Vnfm__authPassword
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if is_vm_vnfm == 'TRUE':
            connection = get_VMVNFM_host_connection()
            cmd = "sudo -E vnflcm oss passwd"
            command = get_vmvnfm_pod_cmd(cmd)
        else:
            connection = ServerConnection.get_connection(server_ip, username, password)
            command = 'sudo -i vnflcm oss passwd'

        interact = connection.invoke_shell()
        resp = interact.recv(9999)
        buff = str(resp)

        # if 'UNIX password:' in buff :
        interact.send(command + '\n')
        time.sleep(10)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'New password:' in buff:
            interact.send(new_password + '\n')
        time.sleep(7)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        log.info('output - %s', str(buff))
        if 'Retype new password' in buff:
            interact.send(new_password + '\n')
        else:
            Report_file.add_line('Could not find Retype new password in the output.')
            log.info('Could not find Retype new password in the output.')
            assert False
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'Operation performed successfully' in buff:
            interact.shutdown(2)
            connection.close()
            log.info('Finished updating vnflcm oss password ')
            Report_file.add_line('Finished updating vnflcm oss password ')

        else:
            log.info('Could not find "Operation performed successfully" in the output')
            Report_file.add_line('Could not find "Operation performed successfully" in the output')
            assert False

    except Exception as error:
        connection.close()
        log.info('Error updating vnflcm oss password %s', str(error))
        Report_file.add_line('Error updating vnflcm oss password ' + str(error))
        assert False


def transfer_node_software(node_name, software_path, node_version, hot_file):
    try:
        log.info('start transferring %s software ', node_name)
        Report_file.add_line('start transferring ' + node_name + ' software ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        log.info('connecting with lcm to remove folder')

        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

        log.info('remove the old folder if exists,path /vnflcm-ext/current/vnf_package_repo/')

        command = 'sudo -i rm -rf /vnflcm-ext/current/vnf_package_repo/' + node_version

        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(5)

        log.info('closing lcm connection after removing folder')

        connection.close()

        log.info('connecting with ecm to transfer folder')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        source_filepath = software_path + '/' + node_version
        destination_filepath = '/vnflcm-ext/current/vnf_package_repo/'

        log.info('Copying %s to lcm server', source_filepath)
        Report_file.add_line('Copying ' + source_filepath + ' to lcm server')

        filepath = '/' + ecm_username + '/'
        ServerConnection.transfer_folder_between_remote_servers(
            connection,
            lcm_server_ip,
            lcm_username,
            lcm_password,
            source_filepath,
            destination_filepath,
            filepath,
            'put',
        )

        log.info('Transferring of %s completed ', source_filepath)
        Report_file.add_line('Transferring of ' + source_filepath + ' completed')
        log.info('closing ecm connection after removing folder')
        connection.close()
        log.info('connecting with lcm for jboss permission')

        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

        command = (
                'sudo -i chown -R jboss_user:jboss /vnflcm-ext/current/vnf_package_repo/'
                + node_version
                + '/Resources/'
        )
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(3)
        command = (
                'sudo -i chown jboss_user:jboss /vnflcm-ext/current/vnf_package_repo/'
                + node_version
                + '/'
                + hot_file
        )
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(3)

        log.info('Extraction and changing ownership completed ')
        Report_file.add_line('Extraction and changing ownership completed')

        log.info('closing lcm connection after jboss permission')

        connection.close()

    except Exception as error:

        connection.close()
        log.info('Error Transferring of Software %s', str(error))
        Report_file.add_line('Error Transferring of Software' + str(error))
        assert False


def check_if_dir_exist_or_not(vnfd_id, destination_filepath):
    try:
        log.info('Start to check if directory exist or not %s', vnfd_id)
        Report_file.add_line('Start to check if directory exist or not ' + vnfd_id)
        dir_chk_path = destination_filepath + vnfd_id
        cmd = 'ls -d ' + dir_chk_path
        dir_connection = get_VMVNFM_host_connection()
        stdin, stdout, stderr = dir_connection.exec_command(cmd)
        command_out = str(stdout.read())
        if vnfd_id in command_out:
            rm_file_path = 'rm -rf ' + dir_chk_path
            stdin, stdout, stderr = dir_connection.exec_command(rm_file_path)
            cmd_out = str(stdout.read())
            if '' in cmd_out:
                Report_file.add_line('File has been deleted successfully' + vnfd_id)
        else:
            Report_file.add_line('File does not exist on the director vm ' + vnfd_id)


    except Exception as error:
        log.info('Error while checking for directory: %s', error)
        Report_file.add_line('Error while checking for directory')
    finally:
        dir_connection.close()


def transfer_node_software_vm_vnfm(node_name, software_path, vnfd_id):
    # e.g - software_path = /var/tmp/deployEPG2.11
    try:
        log.info('start transferring %s software package to VM-VNFM ', node_name)
        Report_file.add_line('start transferring ' + node_name + ' software package to VM-VNFM ')

        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        (
            vm_vnfm_director_ip,
            vm_vnfm_director_username,
        ) = Server_details.vm_vnfm_director_details(Server_details)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if vm_vnfm_namespace == 'codeploy':
            # ServerConnection.put_file_sftp(connection, 'id_rsa_tf.pem', '/root/id_rsa_tf.pem')
            file_path = 'id_rsa_tf.pem'

        else:
            # ServerConnection.put_file_sftp(connection, 'eccd-2-3.pem', '/root/eccd-2-3.pem')
            file_path = 'eccd-2-3.pem'

        path = software_path
        log.info('Transfering package to director server')

        # command to clear the ip from ssh_host file
        remove_ip = 'ssh-keygen -R {}'.format(vm_vnfm_director_ip)
        connection.exec_command(remove_ip)

        package_path = path + '/' + vnfd_id
        log.info(package_path)

        source_filepath = package_path
        destination_filepath = '/home/' + vm_vnfm_director_username + '/'
        check_if_dir_exist_or_not(vnfd_id, destination_filepath)
        log.info('Copying %s file to - %s', source_filepath, vm_vnfm_director_ip)
        Report_file.add_line('Copying ' + source_filepath + ' file to - ' + vm_vnfm_director_ip)

        ServerConnection.transfer_files_with_an_encrypted_pem_file(
            connection,
            file_path,
            source_filepath,
            vm_vnfm_director_username,
            vm_vnfm_director_ip,
            destination_filepath,
        )

        connection.close()

        log.info('Transferred package to director server')

        dir_connection = get_VMVNFM_host_connection()
        source = '/home/{}/{}'.format(vm_vnfm_director_username, vnfd_id)
        destination = '/vnflcm-ext/current/vnf_package_repo/{}'.format(vnfd_id)
        transfer_director_file_to_vm_vnfm(dir_connection, source, destination)

        log.info('waiting 30 seconds to transfer the package to VM-VNFM ')
        time.sleep(30)

        path = '/vnflcm-ext/current/vnf_package_repo/' + vnfd_id

        hot_file = get_file_name_from_vm_vnfm(dir_connection, '.yaml', path)

        log.info('changing the ownership to jboss of the Resources directory and hot file  ')
        Report_file.add_line('changing the ownership to jboss of the Resources directory and hot file')

        chown_and_file_permission(dir_connection, f'{path}/Resources/', "777", "jboss_user")

        chown_and_file_permission(dir_connection, f'{path}/{hot_file}', "777", "jboss_user", recursive=False)

        log.info('Transferring of Software package completed  ')
        Report_file.add_line('Transferring of Software package completed')

    except FileNotFoundError:
        log.error('Path Not Found Error : Wrong file or file path : %s', package_path)
        assert False

    except Exception as error:

        log.info('Error Transferring of Software package  %s', str(error))
        Report_file.add_line('Error Transferring of Software package ' + str(error))
        assert False
    finally:
        dir_connection.close()


def transfer_workflow_rpm_vm_vnfm(node_name, software_path):
    """
    Copy rpm and xml files from blade to VM-VNFM
    software_path = e.g. /var/tmp/deployTOSCAEPG3.14   - refers to location on blade
    """
    try:
        log.info('start transferring %s workflow rpm to VM-VNFM', node_name)
        Report_file.add_line(f'start transferring {node_name} workflow rpm to VM-VNFM')

        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        (
            vm_vnfm_director_ip,
            vm_vnfm_director_username,
        ) = Server_details.vm_vnfm_director_details(Server_details)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if vm_vnfm_namespace == 'codeploy':
            # ServerConnection.put_file_sftp(connection, 'id_rsa_tf.pem', '/root/id_rsa_tf.pem')
            pem_file_path = 'id_rsa_tf.pem'

        else:
            # ServerConnection.put_file_sftp(connection, 'eccd-2-3.pem', '/root/eccd-2-3.pem')
            pem_file_path = 'eccd-2-3.pem'

        log.info('Transfering rpm package to director server')

        # command to clear the ip from ssh_host file
        remove_ip = 'ssh-keygen -R {}'.format(vm_vnfm_director_ip)
        connection.exec_command(remove_ip)

        get_rpm_name = f'ls {software_path}| grep -i .rpm'
        stdin, stdout, stderr = connection.exec_command(get_rpm_name)
        rpm_name = stdout.read().decode('utf-8').strip()

        error_output = stderr.read().decode('utf-8')
        if error_output:
            log.error('Error message : %s', error_output)
            Report_file.add_line(error_output)
            assert False

        rpm_path = f'{software_path}/{rpm_name}'
        log.info(rpm_path)

        source_filepath = rpm_path
        destination_filepath = f'/home/{vm_vnfm_director_username}/'

        log.info('Copying %s file to %s', source_filepath, vm_vnfm_director_ip)
        Report_file.add_line(f'Copying {source_filepath} file to  {vm_vnfm_director_ip}')

        ServerConnection.transfer_files_with_an_encrypted_pem_file(
            connection,
            pem_file_path,
            source_filepath,
            vm_vnfm_director_username,
            vm_vnfm_director_ip,
            destination_filepath,
        )

        log.info('Transfering xml file to director server')
        get_xml_name = f'ls {software_path}| grep -i "ericsson_templ[A-Za-z0-9]*.xml"'
        stdin, stdout, stderr = connection.exec_command(get_xml_name)

        xml_file_name = stdout.read().decode('utf-8').strip()

        error_output = stderr.read().decode('utf-8')
        if error_output:
            log.error('Error message : %s', error_output)
            Report_file.add_line(error_output)
            assert False

        source_filepath = f'{software_path}/{xml_file_name}'

        log.info('Copying %s file to - %s', source_filepath, vm_vnfm_director_ip)
        Report_file.add_line('Copying ' + source_filepath + ' file to - ' + vm_vnfm_director_ip)

        ServerConnection.transfer_files_with_an_encrypted_pem_file(
            connection,
            pem_file_path,
            source_filepath,
            vm_vnfm_director_username,
            vm_vnfm_director_ip,
            destination_filepath,
        )

        connection.close()

        log.info('Transferred package to director server')

        # Copy rpm file from director user home folder to
        # /vnflcm-ext/current/vnf_package_repo/vnf_id
        dir_connection = get_VMVNFM_host_connection()
        set_templ_permissions = f'chmod 644 {xml_file_name}'
        stdin, stdout, stderr = dir_connection.exec_command(set_templ_permissions)
        source = f'/home/{vm_vnfm_director_username}/{rpm_name}'
        destination = '/vnflcm-ext/current/vnf_package_repo/'

        log.info('Copying %s to %s in %s', source, destination, vm_vnfm_director_ip)
        Report_file.add_line(f'Copying {source} to {destination} in {vm_vnfm_director_ip}')

        transfer_director_file_to_vm_vnfm(dir_connection, source, destination)

        # Copy xml file from director user home folder to /tmp
        source = f'/home/{vm_vnfm_director_username}/{xml_file_name}'
        destination = '/tmp'

        log.info('Copying %s to %s in %s', source, destination, vm_vnfm_director_ip)
        Report_file.add_line(f'Copying {source} to {destination} in {vm_vnfm_director_ip}')

        transfer_director_file_to_vm_vnfm(dir_connection, source, destination)
        if SIT.get_vmvnfm_pod_1(SIT) is not None:
            # This is for HA vmvnfm deployment
            log.info("transfer file on ha 1 vmvnfm pod")
            transfer_director_file_to_vm_vnfm(dir_connection, source, destination, ha_pod=True)

        log.info('Transferring of Software package completed  ')
        Report_file.add_line('Transferring of Software package completed')

    except FileNotFoundError as error:
        log.error('Path Not Found Error : Wrong file or file path : %s', str(error))
        assert False

    except Exception as error:
        log.info('Error Transferring of Software package  %s', str(error))
        Report_file.add_line('Error Transferring of Software package ' + str(error))
        assert False
    finally:
        dir_connection.close()


def unpack_node_software(node_name, node_version, complete_software, resource_software, hot_file):
    try:
        # this method calling is removed from feature file , as there is no tar
        # now.
        log.info('start extracting %s Software Tar ', node_name)
        Report_file.add_line('start extracting ' + node_name + ' Software Tar ')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

        log.info('remove the old folder if exists before untar , path /var/tmp')

        command = 'sudo -i rm -rf /var/tmp/' + node_version

        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(5)

        command = 'tar -xf /var/tmp/' + complete_software + ' -C /var/tmp/'
        log.info(command)
        log.info('waiting 60 seconds to un tar file')
        time.sleep(60)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        log.info(command_output)

        if 'No space left on device' in command_output:
            log.info(
                'extract of %s cannot be done as No Space left on device',
                complete_software
            )
            connection.close()
            assert False

        command = 'sudo -i rm -rf /var/tmp/' + complete_software
        log.info(command)
        log.info('Removing the %s after extracting', complete_software)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

        log.info(
            'remove the old folder if exists before untar , '
            'path /vnflcm-ext/current/vnf_package_repo/'
        )

        command = 'sudo -i rm -rf /vnflcm-ext/current/vnf_package_repo/' + node_version

        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(5)

        command = (
                'tar -xf /vnflcm-ext/current/vnf_package_repo/'
                + resource_software
                + ' -C /vnflcm-ext/current/vnf_package_repo/'
        )
        log.info(command)
        log.info('waiting 60 seconds to un tar file')
        time.sleep(60)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        log.info(command_output)
        if 'No space left on device' in command_output:
            log.info('extract of %s cannot be done as No Space left on device', resource_software)
            connection.close()
            assert False

        command = 'sudo -i rm -rf /vnflcm-ext/current/vnf_package_repo/' + resource_software
        log.info(command)
        log.info('Removing the %s after extracting', resource_software)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

        log.info('Extracting of Software Tar completed  ')
        Report_file.add_line('Extracting of Software Tar completed ')
        log.info('changing the ownership to jboss of the Resources directory and %s', hot_file)
        Report_file.add_line('changing the ownership to jboss of the Resources directory and ' + hot_file)

        command = (
                'sudo -i chown -R jboss_user:jboss /vnflcm-ext/current/vnf_package_repo/'
                + node_version
                + '/Resources/'
        )
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(3)
        command = (
                'sudo -i chown jboss_user:jboss /vnflcm-ext/current/vnf_package_repo/'
                + node_version
                + '/'
                + hot_file
        )
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(3)

        log.info('Extraction and changing ownership completed ')
        Report_file.add_line('Extraction and changing ownership completed')

        connection.close()
    except Exception as error:
        connection.close()
        log.info('Error Extraction and changing ownership %s', str(error))
        Report_file.add_line('Error Extraction and changing ownership ' + str(error))
        assert False


def ssh_key_generate_on_lcm(path='/vnflcm-ext/backups/workflows/vnfd/vepc/.ssh/id_rsa'):
    try:
        log.info('start to generate ssh keys from Jboss user')
        Report_file.add_line('start to generate ssh keys from Jboss user')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if is_vm_vnfm == 'TRUE':
            connection = get_VMVNFM_host_connection()
            cmd = "sudo -E su - jboss_user"
            command = get_vmvnfm_pod_cmd(cmd)

        else:
            connection = ServerConnection.get_connection(server_ip, username, password)
            command = 'sudo -i su - jboss_user'

        interact = connection.invoke_shell()
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        command_1 = 'ssh-keygen -t rsa'
        interact.send(command_1 + '\n')
        time.sleep(5)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if 'save the key' in buff:
            interact.send(path + '\n')
            time.sleep(5)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if 'Overwrite' in buff:
            interact.send('n' + '\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

        if 'Enter passphrase' in buff:
            interact.send('\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

        if 'Enter same passphrase' in buff:
            interact.send('\n')
            time.sleep(5)

        interact.shutdown(2)

        log.info('Finished to generate ssh keys from Jboss user')
        Report_file.add_line('Finished to generate ssh keys from Jboss user')

    except Exception as error:

        log.info('Error to generate ssh keys from Jboss user %s', str(error))
        Report_file.add_line('Error to generate ssh keys from Jboss user ' + str(error))
        assert False
    finally:
        connection.close()


def ssh_key_dir(connection, node_version, path):
    try:
        log.info('copying the id_rsa.pub key to the path %s', path)
        Report_file.add_line('copying the id_rsa.pub key to the path ' + path)
        length = len(node_version)
        index = path.index(node_version)
        x_path = path[: index + length:]
        list_of_words = path.split('/')
        next_word = list_of_words[list_of_words.index(node_version) + 1:]
        for word in next_word:
            if word != '':
                x_path = x_path + '/' + word
                command = 'sudo -i mkdir ' + x_path
                stdin, stdout, stderr = connection.exec_command(command)

        command = 'sudo -i cp /home/jboss_user/.ssh/id_rsa.pub ' + path
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(2)
        log.info('copied the id_rsa.pub key to the path %s', path)
        Report_file.add_line('copied the id_rsa.pub key to the path ' + path)
        connection.close()

    except Exception as error:
        log.error('Error directory creation for ssh-key %s %s ', path, str(error))
        Report_file.add_line('Error ssh-key  ' + path + str(error))
        connection.close()
        assert False


def onboard_node_package(onboard_file, upload_file, package_name):
    try:

        log.info('start onboarding package for %s', package_name)
        Report_file.add_line('start onboarding package for ' + package_name)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('curl command of generating package id ')
        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/vnf_packages{}'''.format(
            token, onboard_file, core_vm_hostname, "'"
        )

        Report_file.add_line('Curl command for generating package id ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('Fetching vnfPackage Id for OnBoarding')
        Report_file.add_line('Fetching vnfPackage Id for OnBoarding')
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']
        vnfPackage_id = ''
        if 'SUCCESS' in requestStatus:
            vnfPackage_id = output['data']['vnfPackage']['id']
            # update_runtime_env_file('EPG_PACKAGE_ID',vnfPackage_id)
            log.info('vnfPackage id is : %s', vnfPackage_id)
            log.info('package created successfully for %s', package_name)
            Report_file.add_line('Executed the curl command for creation of package : ' + vnfPackage_id)
            Report_file.add_line('Created package successfully')

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for creating the package %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for creating the package ' + package_name)
            connection.close()
            assert False

        if 'mme' in onboard_file:
            sit_data._SIT__mme_packageId = vnfPackage_id
        else:
            sit_data._SIT__vnf_packageId = vnfPackage_id

        if vnfPackage_id != '':
            log.info('Creating the curl command of uploading the package')

            file_checksum = Common_utilities.crc(
                Common_utilities,
                r'com_ericsson_do_auto_integration_files/' + upload_file,
            )
            data = (
                    '"{\\"chunkSize\\":\\"$(wc -c < ' \
                    + upload_file + ')\\",\\"fileChecksum\\":\\"' \
                    + file_checksum + '\\",\\"chunkData\\":\\"$(base64 ' \
                    + upload_file + ')\\"}"'
            )

            command = f'cd {SIT.get_base_folder(SIT)}; echo {data} > package_input.base64.req.body'
            log.info('command to create package_input.base64.req.body file %s', command)
            connection.exec_command(command)
            tenant_name = sit_data._SIT__tenantName
            command = '''curl --insecure -X PUT "https://{}:443/ecm_service/vnf_packages/{}/content" --header "AuthToken:{}" --header "Content-Range: bytes 0-$(expr $(wc -c < {}) - 1)/$(wc -c < {})" --header "tenantId:{}" --header "Content-Type: application/json" --data @package_input.base64.req.body'''.format(
                core_vm_hostname,
                vnfPackage_id,
                token,
                upload_file,
                upload_file,
                tenant_name,
            )

            Report_file.add_line('Curl command for uploading the package ' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            output = ast.literal_eval(command_output[2:-1:1])
            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:
                log.info('package %s uploaded successfully.', vnfPackage_id)
                Report_file.add_line(
                    'Uploaded package successfully. Verifying the status of provisioning and operationalState.')
                Common_utilities.create_artifact_prop_file(Common_utilities,
                                                           [vnfPackage_id], 'ETSI_TOSCA_EPG_INSTALL')

            elif 'ERROR' in requestStatus:
                command_error = output['status']['msgs'][0]['msgText']

                log.error('Error executing curl command for uploading the package %s', command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command for uploading the package')
                connection.close()
                assert False

        else:
            log.info('VNF-Package Id not found %s', vnfPackage_id)
            Report_file.add_line('VNF-Package Id not found ' + vnfPackage_id)

    except Exception as error:
        connection.close()
        log.error('Error onboarding package %s', str(error))
        Report_file.add_line('Error onboarding package ' + str(error))
        assert False


def deploy_node(deploy_file, node_name=''):
    try:

        log.info('start deploying node with file %s', deploy_file)
        Report_file.add_line('start deploying node with file ' + deploy_file)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        vnfPackage_id = ''

        if node_name == 'MME':
            vnfPackage_id = sit_data._SIT__mme_packageId

        else:
            vnfPackage_id = sit_data._SIT__vnf_packageId

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken: {}' --data @{} 'https://{}/ecm_service/vnfpackages/{}/deploy{}'''.format(
            token, deploy_file, core_vm_hostname, vnfPackage_id, "'")

        Report_file.add_line('curl command of deployment ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('Saving the correlation id for fetching the vApp id')
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            correlation_id = output['correlationId']
            log.info('correlation_id : %s', correlation_id)
            Report_file.add_line('correlation_id : ' + correlation_id)
            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities,
                connection,
                token,
                core_vm_hostname,
                correlation_id,
                60,
            )

            if order_status:
                log.info('Saving the vApp id')

                requestStatus = order_output['status']['reqStatus']

                if 'SUCCESS' in requestStatus:

                    node_id = order_output['data']['order']['orderItems'][0]['deployVnfPackage']['id']
                    log.info('deployed Vnf package id  : %s', node_id)
                    Report_file.add_line('deployed Vnf package id   : ' + node_id)
                    sit_data.set_vapp_Id(sit_data, node_id)
                    sit_data._SIT__vapp_Id = node_id
                    log.info('node deployed successfully. Verifying the Ping Response of '
                             'external_ip_for_services_vm and status of provisioning and operational')
                    connection.close()

                elif 'ERROR' in requestStatus:

                    command_error = order_output['status']['msgs'][0]['msgText']

                    log.error('Error executing curl command for Deploying the node %s', command_error)
                    Report_file.add_line(command_error)
                    Report_file.add_line('Error executing curl command for Deploying the node')
                    raise ValueError('Error executing curl command for Deploying the node ')

            else:

                log.info('Order Status is failed with message mentioned above %s', correlation_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + correlation_id)
                raise ValueError('Order Status is Failed ')

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for Deploying the package %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for Deploying the node')
            raise ValueError('Error executing curl command for Deploying the node ')

    except Exception as error:
        connection.close()
        log.error('Error deploying package %s', str(error))
        Report_file.add_line('Error deploying package ' + str(error))
        assert False


def onboard_node_hot_package(package_name, upload_file, software_path):
    try:

        log.info('start onboarding package for %s', package_name)
        Report_file.add_line('start onboarding package for ' + package_name)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.get_file_sftp(
            connection,
            software_path + '/' + upload_file,
            r'com_ericsson_do_auto_integration_files/' + upload_file,
        )
        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/' + upload_file,
            SIT.get_base_folder(SIT) + upload_file,
        )

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        log.info('Creating the curl command of uploading the package')

        file_checksum = Common_utilities.crc(
            Common_utilities, r'com_ericsson_do_auto_integration_files/' + upload_file
        )
        chunk_size = '$(wc -c < {})'.format(upload_file)
        chunk_data = '$(base64 {})'.format(upload_file)
        tenant_name = sit_data._SIT__tenantName
        data = (
                '"{\\"tenantName\\":\\"'
                + tenant_name
                + '\\",\\"package\\":{\\"fileName\\":\\"'
                + upload_file
                + '\\",\\"description\\":\\"onboard package\\",\\"isPublic\\":false,\\"name\\":\\"'
                + package_name
                + '\\",\\"fileChecksum\\":\\"'
                + file_checksum
                + '\\",\\"chunkSize\\":\\"'
                + chunk_size
                + '\\",\\"familyTag\\":\\"\\",\\"chunkData\\":\\"'
                + chunk_data
                + '\\" }}"'
        )
        command = f'cd {SIT.get_base_folder(SIT)}; echo {data} > package_hot.base64.req.body'
        log.info('command to create package_hot.base64.req.body file %s', command)
        connection.exec_command(command)

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header "Content-Range: bytes 0-$(expr $(wc -c < {}) - 1)/$(wc -c < {})"  --header 'Accept: application/json' --header 'AuthToken:{}' --data @package_hot.base64.req.body 'https://{}/ecm_service/hotpackages{}'''.format(
            upload_file, upload_file, token, core_vm_hostname, "'")

        Report_file.add_line('Curl command for uploading the package ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            vnfPackage_id = output['data']['package']['id']
            sit_data._SIT__vnf_packageId = vnfPackage_id
            log.info('package %s uploaded successfully.', vnfPackage_id)
            Report_file.add_line('Uploaded package successfully.')

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for uploading the package %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for uploading the package')
            connection.close()
            assert False

    except Exception as error:
        connection.close()
        log.error('Error onboarding package %s', str(error))
        Report_file.add_line('Error onboarding package ' + str(error))
        assert False


def deploy_node_hot_package(deploy_file):
    try:

        log.info('start deploying node/network hot package/template with file %s', deploy_file)
        Report_file.add_line('start deploying node/template hot package/template with file ' + deploy_file)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + deploy_file,
                                       SIT.get_base_folder(SIT) + deploy_file)
        vnfPackage_id = sit_data._SIT__vnf_packageId
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/hotpackages/{}/deploy{}'''.format(
            token, deploy_file, core_vm_hostname, vnfPackage_id, "'")

        Report_file.add_line('curl command of deployment ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('Saving the correlation id for fetching the vApp id')
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            correlation_id = output['data']['order']['id']
            log.info('correlation_id : %s', correlation_id)
            Report_file.add_line('correlation_id : ' + correlation_id)
            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities,
                connection,
                token,
                core_vm_hostname,
                correlation_id,
                60,
            )

            if order_status:
                log.info('Saving the vApp id')

                requestStatus = order_output['status']['reqStatus']

                if 'SUCCESS' in requestStatus:

                    node_id = order_output['data']['order']['orderItems'][0]['deployHotPackage']['id']
                    log.info('deployed Vnf package id  : %s', node_id)
                    Report_file.add_line('deployed Vnf package id   : ' + node_id)
                    sit_data.set_vapp_Id(sit_data, node_id)
                    sit_data._SIT__vapp_Id = node_id
                    log.info('node deployed successfully.verifying status of provisioning ')
                    connection.close()

                elif 'ERROR' in requestStatus:

                    command_error = order_output['status']['msgs'][0]['msgText']

                    log.error('Error executing curl command for Deploying the node %s', command_error)
                    Report_file.add_line(command_error)
                    Report_file.add_line('Error executing curl command for Deploying the node')
                    connection.close()
                    assert False

            else:

                log.info('Order Status is failed with message mentioned above %s', correlation_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + correlation_id)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for Deploying the package %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for Deploying the node')
            connection.close()
            assert False

    except Exception as error:
        connection.close()
        log.error('Error deploying node/network hot package/template %s', str(error))
        Report_file.add_line('Error deploying node/network hot package/template ' + str(error))
        assert False


def deploy_network_env_yaml(software_path, deploy_file, network_name):
    try:

        log.info('start deploying network with file %s', deploy_file)
        Report_file.add_line('start deploying network with file ' + deploy_file)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vnfPackage_id = sit_data._SIT__vnf_packageId

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        command = f'cp {software_path}/{deploy_file} {SIT.get_base_folder(SIT)}'
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command)

        chunk_data = '$(base64 {})'.format(deploy_file)
        tenant_name = sit_data._SIT__tenantName
        vimzone_name = sit_data._SIT__vimzone_name
        vdc_id = sit_data._SIT__vdc_id

        data = (
                '"{\\"tenantName\\":\\"'
                + tenant_name
                + '\\",\\"vimZoneName\\":\\"'
                + vimzone_name
                + '\\",\\"vdc\\":{\\"id\\":\\"'
                + vdc_id
                + '\\"},\\"hotPackage\\":{\\"vapp\\":{\\"name\\":\\"'
                + network_name
                + '\\",\\"configDataEnvFile\\":[{\\"fileName\\":\\"'
                + deploy_file
                + '\\",\\"fileContent\\":\\"'
                + chunk_data
                + '\\"}]}}}"'
        )

        command = f'cd {SIT.get_base_folder(SIT)}; echo {data} > network_package_input.base64.req.body'
        log.info('command to create network_package_input.base64.req.body file %s', command)
        stdin, stdout, stderr = connection.exec_command(command)
        time.sleep(2)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = '''curl --insecure "https://{}/ecm_service/hotpackages/{}/deploy" -H "AuthToken: {}" -H "Accept: application/json" -H "Content-Type: application/json" --data @network_package_input.base64.req.body'''.format(
            core_vm_hostname, vnfPackage_id, token)
        Report_file.add_line('curl command of network deployment ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('Saving the correlation id for fetching the vApp id')
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            log.info('order_id : %s', order_id)
            Report_file.add_line('order_id : ' + order_id)
            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities, connection, token, core_vm_hostname, order_id, 60
            )

            if order_status:

                requestStatus = order_output['status']['reqStatus']

                if 'SUCCESS' in requestStatus:

                    log.info('order completed for deployed network package')
                    Report_file.add_line('order completed for deployed network package')
                    log.info('network deployed successfully.')
                    connection.close()

                elif 'ERROR' in requestStatus:

                    command_error = order_output['status']['msgs'][0]['msgText']

                    log.error('Error executing curl command for Deploying the network %s', command_error)
                    Report_file.add_line(command_error)
                    Report_file.add_line('Error executing curl command for Deploying the network')
                    connection.close()
                    assert False

            else:

                log.info('Order Status is failed with message mentioned above %s', order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for Deploying the network %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for Deploying the network')
            connection.close()
            assert False

    except Exception as error:
        connection.close()
        log.error('Error deploying network %s', str(error))
        Report_file.add_line('Error deploying network ' + str(error))
        assert False


def deploy_sbg_network_env_yaml(software_path, deploy_file, deploy_file2, network_name):
    try:

        log.info('start deploying SBG network with file %s', deploy_file)
        Report_file.add_line('start deploying SBG network with file ' + deploy_file)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vnfPackage_id = sit_data._SIT__vnf_packageId

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        command = f'cp {software_path}/{deploy_file} {SIT.get_base_folder(SIT)}'
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command)

        time.sleep(2)

        command = f'cp {software_path}/{deploy_file2} {SIT.get_base_folder(SIT)}'
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command)

        chunk_data = '$(base64 {})'.format(deploy_file)
        tenant_name = sit_data._SIT__tenantName
        vimzone_name = sit_data._SIT__vimzone_name
        vdc_id = sit_data._SIT__vdc_id
        chunk_data2 = '$(base64 {})'.format(deploy_file2)
        deplyfile2_path = 'Resources/HotFiles/' + deploy_file2

        data = (
                '"{\\"tenantName\\":\\"'
                + tenant_name
                + '\\",\\"vimZoneName\\":\\"'
                + vimzone_name
                + '\\",\\"vdc\\":{\\"id\\":\\"'
                + vdc_id
                + '\\"},\\"hotPackage\\":{\\"vapp\\":{\\"name\\":\\"'
                + network_name
                + '\\",\\"configFiles\\":[{\\"fileId\\":\\"'
                + deplyfile2_path
                + '\\",\\"fileContent\\":\\"'
                + chunk_data2
                + '\\"}],\\"configDataEnvFile\\":[{\\"fileName\\":\\"'
                + deploy_file
                + '\\",\\"fileContent\\":\\"'
                + chunk_data
                + '\\"}]}}}"'
        )

        command = f'cd {SIT.get_base_folder(SIT)}; echo {data} > network_package_input.base64.req.body'
        log.info('command to create network_package_input.base64.req.body file %s', command)
        stdin, stdout, stderr = connection.exec_command(command)
        time.sleep(2)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = '''curl --insecure "https://{}/ecm_service/hotpackages/{}/deploy" -H "AuthToken: {}" -H "Accept: application/json" -H "Content-Type: application/json" --data @network_package_input.base64.req.body'''.format(
            core_vm_hostname, vnfPackage_id, token)
        Report_file.add_line('curl command of network deployment ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('Saving the correlation id for fetching the vApp id')
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            log.info('order_id : %s', order_id)
            Report_file.add_line('order_id : ' + order_id)
            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities, connection, token, core_vm_hostname, order_id, 60
            )

            if order_status:

                requestStatus = order_output['status']['reqStatus']

                if 'SUCCESS' in requestStatus:

                    log.info('order completed for deployed network package')
                    Report_file.add_line('order completed for deployed network package')
                    log.info('network deployed successfully.')
                    connection.close()

                elif 'ERROR' in requestStatus:

                    command_error = order_output['status']['msgs'][0]['msgText']

                    log.error('Error executing curl command for Deploying the network %s', command_error)
                    Report_file.add_line(command_error)
                    Report_file.add_line('Error executing curl command for Deploying the network')
                    connection.close()
                    assert False

            else:

                log.info('Order Status is failed with message mentioned above %s', order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for Deploying the network %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for Deploying the network')
            connection.close()
            assert False

    except Exception as error:
        connection.close()
        log.error('Error deploying network %s', str(error))
        Report_file.add_line('Error deploying network ' + str(error))
        assert False


def workflow_deployment(path, node_name):
    try:

        log.info('start workflow bundle install on LCM')
        Report_file.add_line('Workflow  bundle install on LCM begins...')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if is_vm_vnfm == 'TRUE':

            log.info('vm vnfm is true')
            (
                vm_vnfm_director_ip,
                vm_vnfm_director_username,
            ) = Server_details.vm_vnfm_director_details(Server_details)
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            if vm_vnfm_namespace == 'codeploy':
                # ServerConnection.put_file_sftp(connection, 'id_rsa_tf.pem', '/root/id_rsa_tf.pem')
                file_path = 'id_rsa_tf.pem'

            else:
                # ServerConnection.put_file_sftp(connection, 'eccd-2-3.pem', '/root/eccd-2-3.pem')
                file_path = 'eccd-2-3.pem'

            log.info('Transferring workflow dir to director server')

            # command to clear the ip from ssh_host file
            remove_ip = 'ssh-keygen -R {}'.format(vm_vnfm_director_ip)
            connection.exec_command(remove_ip)

            source_filepath = path
            destination_filepath = '/home/' + vm_vnfm_director_username + '/'
            log.info('Copying %s file to - %s', source_filepath, vm_vnfm_director_ip)
            Report_file.add_line('Copying ' + source_filepath + ' file to - ' + vm_vnfm_director_ip)

            ServerConnection.transfer_files_with_an_encrypted_pem_file(
                connection,
                file_path,
                source_filepath,
                vm_vnfm_director_username,
                vm_vnfm_director_ip,
                destination_filepath,
            )

            connection.close()

            log.info('Transferred workflow dir to director server')

            rpm_dir = path[9:]

            nested_conn = get_VMVNFM_host_connection()
            director_path = '/home/' + vm_vnfm_director_username + '/' + rpm_dir

            rpmname = get_file_name_from_director_server(nested_conn, '.rpm', director_path)
            log.info('rpm name :%s', rpmname)

            log.info('Transferring workflow rpm to eric-vnflcm-service pod %s', rpmname)

            source = '/home/' + vm_vnfm_director_username + '/' + rpm_dir + '/' + rpmname
            destination = f'/tmp/{rpmname}'

            transfer_director_file_to_vm_vnfm(nested_conn, source, destination)

            time.sleep(20)
            cmd = f"sudo -E wfmgr bundle install --package={destination}"
            command = get_vmvnfm_pod_cmd(cmd)

            vm_vnfm_lcm_workflow_installation_validation(nested_conn, command, node_name)
            Common_utilities.clean_up_rpm_packages(Common_utilities, nested_conn, rpmname)

        else:

            log.info('Connecting to ECM blade to transfer workflow to VNF-LCM')
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            source_filepath = path
            destination_filepath = '/var/tmp/'

            filepath = '/' + ecm_username + '/'

            # command to clear the ip from ssh_host file
            remove_ip = 'ssh-keygen -R {}'.format(lcm_server_ip)
            connection.exec_command(remove_ip)

            ServerConnection.transfer_folder_between_remote_servers(
                connection,
                lcm_server_ip,
                lcm_username,
                lcm_password,
                source_filepath,
                destination_filepath,
                filepath,
                'put',
            )

            connection.close()

            log.info('Connecting to VNF-LCM to Install workflow')
            connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

            # command to list the latest time stamp rpm bundle
            log.info('fetching the latest workflow in %s on VNF-LCM', path)
            command = 'cd ' + path + ' ; find . -type f | xargs grep -l .rpm | xargs ls -rt | tail -1'
            log.info(command)
            stdin, stdout, stderr = connection.exec_command(command)
            command_output = stdout.read().decode('utf-8')
            log.info('command output  : %s', command_output)

            output = str(command_output).split('\n')[0]
            rpm_name = output.split('./')[1]

            log.info('rpm name :%s', rpm_name)

            action, attr_list = check_workflow_exists(connection, 'GenericWorkflows', node_name, rpm_name)

            if action == 'uninstall':
                command = '''sudo -i wfmgr bundle uninstall --name {} --version {} --package {}'''.format(
                    'GenericWorkflows', attr_list[2].strip(), attr_list[3].strip()
                )
                LCM_workflow_uninstallation_validation(command, node_name)

            command = 'sudo -i wfmgr bundle install --package={}/{}'.format(path, rpm_name)
            LCM_workflow_installation_validation(connection, command, node_name)
            Common_utilities.clean_up_rpm_packages(Common_utilities, connection, rpm_name)

            connection.close()

    except Exception as error:
        connection.close()
        log.info('Error workflow bundle install on LCM %s', str(error))
        Report_file.add_line('Error workflow bundle install on LCM ' + str(error))
        assert False


def ims_workflow_deployment():
    ims_workflow_path = r'/var/tmp/IMS_WORKFLOW'
    workflow_deployment(ims_workflow_path, 'IMS')


# This is the new method when node artifects are being created automatically for IMS Nodes
# This also can be used for EPG and MME node once their artefects ctreats
# autoamtically


def transfer_node_software_vnflcm(node_name, software_dir):
    try:
        log.info('start transferring %s software package to vnf_lcm server ', node_name)
        Report_file.add_line('start transferring ' + node_name + ' software package to vnf_lcm server ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        vnfd_id = sit_data._SIT__ims_vnfd_id

        lcm_connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
        log.info('Going to remove if package %s already exists', vnfd_id)
        termiante_path = '/vnflcm-ext/current/vnf_package_repo/' + vnfd_id

        command = f'sudo -i rm -rf {termiante_path}'
        Report_file.add_line('Remove Command : ' + command)
        stdin, stdout, stderr = lcm_connection.exec_command(command, get_pty=True)
        command_output = str(stdout.read())
        Report_file.add_line('Command Output : ' + command_output)

        lcm_connection.close()

        time.sleep(2)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        path = '/var/tmp/{}/'.format(software_dir)

        package_path = path + vnfd_id
        log.info(package_path)

        source_filepath = package_path
        destination_filepath = '/vnflcm-ext/current/vnf_package_repo/'

        Report_file.add_line('Copying ' + source_filepath + ' to  lcm server')

        filepath = '/' + ecm_username + '/'
        ServerConnection.transfer_folder_between_remote_servers(
            connection,
            lcm_server_ip,
            lcm_username,
            lcm_password,
            source_filepath,
            destination_filepath,
            filepath,
            'put',
        )

        connection.close()

        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

        command = 'cd {};ls -ltr | grep -i .yaml'.format(path)

        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        Report_file.add_line('command_output : ' + command_output)
        hot_file = output[-1][:-3]
        log.info('hot file  name for node %s : %s', node_name, hot_file)

        log.info('changing the ownership to jboss of the Resources directory and hot file  ')
        Report_file.add_line('changing the ownership to jboss of the Resources directory and hot file')

        command = (
                'sudo -i chown -R jboss_user:jboss /vnflcm-ext/current/vnf_package_repo/'
                + vnfd_id
                + '/Resources/'
        )
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(3)
        command = (
                'sudo -i chown jboss_user:jboss /vnflcm-ext/current/vnf_package_repo/' + vnfd_id + '/' + hot_file
        )
        log.info(command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(3)

        log.info('Transferring of Software package completed  ')
        Report_file.add_line('Transferring of Software package completed')

    except FileNotFoundError:
        log.error('Path Not Found Error : Wrong file or file path : %s', package_path)
        assert False

    except Exception as error:
        log.info('Error Transferring of Software package  %s', str(error))
        Report_file.add_line('Error Transferring of Software package ' + str(error))
        assert False
    finally:
        connection.close()


def transfer_workflow_rpm_vnflcm(node_name, software_dir):
    """
    Copy rpm and xml files from blade to VM-VNFM
        software_path = e.g. /var/tmp/deployEPG2.11
    """
    try:
        log.info('start transferring %s workflow rpm to vnf_lcm server', node_name)
        Report_file.add_line(f'start transferring {node_name} workflow rpm to vnf_lcm server')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        get_rpm_name = f"ls {software_dir}| grep -i .rpm"
        stdin, stdout, stderr = connection.exec_command(get_rpm_name)
        handle_stderr(stderr, log)

        rpm_name = stdout.read().decode('utf-8').strip()

        source_filepath = f'{software_dir}/{rpm_name}'
        destination_filepath = '/vnflcm-ext/current/vnf_package_repo/'

        log.info('Copying %s to lcm server %s', source_filepath, destination_filepath)
        Report_file.add_line(f'Copying {source_filepath} to  lcm server {destination_filepath}')

        filepath = f'/{ecm_username}/'
        ServerConnection.transfer_folder_between_remote_servers(
            connection,
            lcm_server_ip,
            lcm_username,
            lcm_password,
            source_filepath,
            destination_filepath,
            filepath,
            'put',
        )

        log.info('transferring xml template to vnf_lcm server')
        get_xml_name = f"ls {software_dir}| grep -i 'ericsson_templ[A-Za-z0-9]*.xml'"

        stdin, stdout, stderr = connection.exec_command(get_xml_name)
        handle_stderr(stderr, log)

        xml_file_name = stdout.read().decode('utf-8').strip()

        source_filepath = f'{software_dir}/{xml_file_name}'
        destination_filepath = '/tmp'

        log.info('Copying %s to lcm server source_filepath %s', source_filepath, destination_filepath)
        Report_file.add_line(f'Copying {source_filepath} to  lcm server {destination_filepath}')

        filepath = f'/{ecm_username}/'
        ServerConnection.transfer_folder_between_remote_servers(
            connection,
            lcm_server_ip,
            lcm_username,
            lcm_password,
            source_filepath,
            destination_filepath,
            filepath,
            'put',
        )

        connection.close()

        log.info('Transferring of Software package completed ')
        Report_file.add_line('Transferring of Software package completed')

    except FileNotFoundError:
        log.error('Path Not Found Error : Wrong file or file path : %s', software_dir)
        assert False

    except Exception as error:

        log.info('Error Transferring of Software package %s ', error)
        Report_file.add_line(f'Error Transferring of Software package {error} ')
        assert False
    finally:
        connection.close()


def get_vnfd_id_ims_nodes(node_name, software_dir):
    log.info('start fetching vnfd id for  %s', node_name)
    Report_file.add_line('start fetching vnfd id for  ' + node_name)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    path = '/var/tmp/{}/'.format(software_dir)
    command = 'cd {};ls -ltr | grep -i .zip'.format(path)

    stdin, stdout, stderr = connection.exec_command(command)
    command_output = str(stdout.read())
    output = command_output.split()
    Report_file.add_line('command_output : ' + command_output)
    vnfd_id = output[-1][:-7]
    log.info('Vnfd id or folder name for node ' + node_name + ' : ' + vnfd_id)

    if vnfd_id == '':
        log.error('vnfdid not found')
        assert False

    sit_data._SIT__ims_vnfd_id = vnfd_id

    log.info('Finished fetching vnfd id for %s', node_name)
    Report_file.add_line('Finished fetching vnfd id for  ' + node_name)


# This method is used to update the supportedpackagetypes to HOT in VNF LCM
def update_workflow_package_hot(connection, lcm_password):
    try:
        log.info('updating supportedpackagetypes to HOT')
        Report_file.add_line('updating supportedpackagetypes to HOT')

        interact = connection.invoke_shell()

        command = 'sudo -i'
        interact.send(command + '\n')
        time.sleep(2)

        command = 'sshdb'
        interact.send(command + '\n')

        time.sleep(6)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if "vnflaf-db's password" in buff:
            interact.send(lcm_password + '\n')
            time.sleep(4)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'Permission denied' in buff:
                log.info('Permission denied , password has been changed . Going to set it again')
                change_db_passwd_when_permission_denied(interact, lcm_password)

        command = '''sudo -u postgres psql -d vnflafdb '''
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        command = 'select * from workflowbundle where name= {}epg_lcm_wf_heat{};'.format("'", "'")
        Report_file.add_line(command)
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)

        log.info(buff)
        output = buff.split(';')

        split_data = output[1]

        output = split_data.split('\\r\\n--------------------------------------')[1]

        output = output.split('\\r\\n')[1].strip()

        workflow_bundle_id = output.split('|')[0].strip()

        Report_file.add_line('workflowbundleid - ' + workflow_bundle_id)

        command = 'select * from workflowbundlesupportedproducts where workflowbundleid ={}{}{};'.format(
            "'", workflow_bundle_id, "'"
        )

        Report_file.add_line(command)
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)

        log.info(buff)

        output = buff.split(';')

        split_data = output[1]

        output = split_data.split('|')[6].strip()

        Report_file.add_line('supportedpackagetypes - ' + output)
        if 'TOSCA,OVF' in output:
            command = 'update workflowbundlesupportedproducts set supportedpackagetypes={}HOT{} where workflowbundleid={}{}{};'.format(
                "'", "'", "'", workflow_bundle_id, "'"
            )
            Report_file.add_line(command)
            interact.send(command + '\n')
            time.sleep(2)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            log.info('db updated')

        interact.shutdown(2)

    except Exception as error:
        log.info('Error updating supportedpackagetypes to HOT %s', str(error))
        Report_file.add_line('Error updating supportedpackagetypes to HOT ' + str(error))
        assert False

    # This method is used to update the supportedpackagetypes to HOT in VM VNFM


def update_workflow_package_hot_vm_vnfm(connection, vm_vnfm_namespace):
    try:
        log.info('updating supportedpackagetypes to HOT in VM VNFM')
        Report_file.add_line('updating supportedpackagetypes to HOT in VM VNFM')

        vmvnfm_version = fetch_vmvnfm_version(connection, vm_vnfm_namespace)
        interact = connection.invoke_shell()
        master_pod = get_master_vnflcm_db_pod(connection)
        command = 'kubectl exec -it {} -n {} -- /bin/bash'.format(master_pod, vm_vnfm_namespace)
        interact.send(command + '\n')
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if vmvnfm_version >= version.parse("2.29.0-3"):
            command = 'psql -U postgres -d vnflafdb'
        else:
            if 'postgres@' not in buff:
                command = 'su postgres'
                interact.send(command + '\n')
                time.sleep(3)
                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
            command = 'psql -d vnflafdb'
        interact.send(command + '\n')
        time.sleep(3)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        command = 'select * from workflowbundle where name= {}epg_lcm_wf_heat{};'.format("'", "'")
        Report_file.add_line(command)
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)

        log.info(buff)

        output = buff.split(';')
        Report_file.add_line(output)

        split_data = output[1]

        output = split_data.split('\\r\\n--------------------------------------')[1]

        output = output.split('\\r\\n')[1].strip()

        workflow_bundle_id = output.split('|')[0].strip()

        Report_file.add_line('workflow_bundle_id - ' + workflow_bundle_id)

        command = 'select * from workflowbundlesupportedproducts where workflowbundleid ={}{}{};'.format(
            "'", workflow_bundle_id, "'"
        )

        Report_file.add_line(command)
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)

        log.info(buff)

        output = buff.split(';')
        Report_file.add_line(output)

        split_data = output[1]

        output = split_data.split('|')[5].strip()

        Report_file.add_line(output)

        if 'TOSCA,OVF' in output:
            command = 'update workflowbundlesupportedproducts set supportedpackagetypes={}HOT{} where workflowbundleid={}{}{};'.format(
                "'", "'", "'", workflow_bundle_id, "'"
            )
            Report_file.add_line(command)
            interact.send(command + '\n')
            time.sleep(2)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            log.info('VM VNFM db updated')

        interact.shutdown(2)

    except Exception as error:

        log.info('Error updating supportedpackagetypes to HOT in VM VNFM %s', str(error))
        Report_file.add_line('Error updating supportedpackagetypes to HOT VM VNFM' + str(error))
        assert False

    # This method is used to install workflows with validation used for IMS,
    # DUMMY<EPG AND MME NODES


def LCM_workflow_installation_validation(connection, command, node_name):
    log.info('Starting Install of LCM Workflow using rpm bundle for node %s', node_name)
    Report_file.add_line('Starting Install of LCM Workflow using rpm bundle for node ' + node_name)

    Report_file.add_line('command for workflow installation  : ' + command)
    stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

    command_output = str(stdout.read())

    Report_file.add_line('command output : ' + command_output)

    if 'already installed' in command_output:

        log.info('LCM Workflow package already installed for node %s', node_name)

    elif 'package installation successful' in command_output:
        log.info('LCM Workflow package installation successful for node %s', node_name)

    else:
        log.error('LCM Workflow package installation failed check command output for details %s', command_output)
        assert False

    log.info('Install of LCM Workflow finished using command:%s', command)
    Report_file.add_line('Install of LCM Workflow finished')


# This method is used to install workflows with validation used for VM
# VNFM LCM POD Server
def vm_vnfm_lcm_workflow_installation_validation(nested_conn, command, node_name):
    log.info('Starting Install of VM VNFM LCM Workflow using rpm bundle for node %s', node_name)
    Report_file.add_line('Starting Install of VM VNFM LCM Workflow using rpm bundle for node ' + node_name)

    Report_file.add_line('command for workflow installation  : ' + command)
    stdin, stdout, stderr = nested_conn.exec_command(command)

    command_output = str(stdout.read())

    Report_file.add_line('command output : ' + command_output)

    if 'already installed' in command_output:

        log.info('VM VNFM LCM Workflow package already installed for node %s', node_name)

    elif 'package installation successful' in command_output:
        log.info('VM VNFM LCM Workflow package installation successful for node %s', node_name)

    else:
        log.error('Vm VNFM LCM Workflow package installation failed check command output for details %s',
                  command_output)
        assert False

    log.info('Install of VM VNFM LCM Workflow finished using command: %s', command)
    Report_file.add_line('Install of VM VNFM  LCM Workflow finished')


def check_workflow_exists(connection, workflow_type, node_name, rpm_name):
    log.info('checking if workflow exists for node %s with type %s', node_name, workflow_type)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
    is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

    given_version = rpm_name.split('-')[1].strip()[:-4:]

    log.info('given version of rpm bundle is %s', given_version)

    if is_vm_vnfm == 'TRUE':
        cmd = f"sudo -E wfmgr bundle list | grep -i {workflow_type}"
        command = get_vmvnfm_pod_cmd(cmd)

    else:
        command = '''sudo -i wfmgr bundle list | grep -i {}'''.format(workflow_type)

    Report_file.add_line('command for workflow check  : ' + command)
    stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

    command_output = str(stdout.read())[2:-1:1]

    Report_file.add_line('command output : ' + command_output)

    if command_output:
        version = command_output.split('|')[2].strip()
        log.info('version found on server is %s', version)

        if version == given_version:
            log.info('workflow with same version is already exists %s', rpm_name)
            return 'skip', ''

        else:
            log.info('workflow with some other version is installed ,version is %s', version)
            return 'uninstall', command_output.split('|')

    else:
        log.info('Workflow does not exists')
        return 'install', ''


def LCM_workflow_uninstallation_validation(command, node_name):
    log.info('Starting un-Install of LCM Workflow using rpm bundle for node %s', node_name)
    Report_file.add_line('Starting un-Install of LCM Workflow using rpm bundle for node ' + node_name)

    Report_file.add_line('command for workflow un-installation  : ' + command)

    lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)

    result = misc.interact_command_ssh(
        command=command,
        expect=b'Are you sure you want to continue(yes/no)?\r\n',
        answer='yes\n',
        timeout=1200,
        hostname=lcm_server_ip,
        username=lcm_username,
        password=lcm_password,
    )

    log.info('command output %s', str(result))
    Report_file.add_line('command output ' + str(result))

    log.info('un-Install of LCM Workflow finished ')
    Report_file.add_line('un-Install of LCM Workflow finished')


def add_package_download_parameter(node_name):
    try:
        log.info('Start Add package download parameter to VNF-LCM CONFIG for %s', node_name)
        Report_file.add_line('Start Add package download parameter to VNF-LCM CONFIG for ' + node_name)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if is_vm_vnfm == 'TRUE':
            log.info(' VM VNFM True , Adding package download parameter ')

            connection = get_VMVNFM_host_connection()
            cmd = "sudo -i /ericsson/pib-scripts/etc/config.py create --app_server_address localhost:8080 --name=packageDownload --value=YES --type=String --scope=GLOBAL"
            command = get_vmvnfm_pod_cmd(cmd)

        else:
            connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            command = 'sudo -i /ericsson/pib-scripts/etc/config.py create --app_server_address localhost:8080 --name=packageDownload --value=YES --type=String --scope=GLOBAL'

        Report_file.add_line('command ' + command)

        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        command_output = str(stdout.read())[2:-1:1]
        Report_file.add_line('command output : ' + command_output)

        log.info('Finished Add package download parameter to VNF-LCM CONFIG for %s', node_name)
        Report_file.add_line('Finished Add package download parameter to VNF-LCM CONFIG for ' + node_name)
    except Exception as error:

        log.error('Error Add package download parameter to VNF-LCM CONFIG for %s', node_name)
        Report_file.add_line('Error Add package download parameter to VNF-LCM CONFIG for ' + node_name)
        assert False
    finally:
        connection.close()


def check_flavor_exists_in_ecm(connection, token, core_vm_hostname, tenant_name, flavor_name):
    try:
        # flavor name -- with out CM-    i.e - Reconcile_SRT_OS
        log.info('Start searching flavor %s  in ECM ', flavor_name)
        Report_file.add_line('Start searching flavor {}  in ECM '.format(flavor_name))

        command = 'curl --insecure "https://{}/ecm_service/srts?$filter=tenantName"%"3D"%"27{}"%"27" -H "Accept: application/json" -H "AuthToken: {}"'.format(
            core_vm_hostname, tenant_name, token)

        Report_file.add_line('Command ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        data_exists = False

        if 'srts' in command_output:
            data_exists = True

        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            if data_exists:
                flavor_list = output['data']['srts']

                for flavor in flavor_list:
                    name = flavor['name']
                    if flavor_name == name:
                        log.info('flavor exists in ECM ')
                        return True

                log.info('flavor does not exists in ECM')
                return False

            else:
                log.info('flavor does not exists in ECM')
                return False

    except Exception as error:

        log.error('Error searching flavor in ECM %s', str(error))
        Report_file.add_line('Error searching flavor in ECM' + str(error))
        assert False


def check_security_group_exists_in_ecm(connection, token, core_vm_hostname, tenant_name, security_group_name):
    try:
        log.info('Start searching security_group %s in ECM', security_group_name)
        Report_file.add_line('Start searching security_group {}  in ECM '.format(security_group_name))

        command = 'curl --insecure "https://{}/ecm_service/v2/securitygroups?$filter=tenantName"%"3D"%"27{}"%"27" -H "Accept: application/json" -H "AuthToken: {}"'.format(
            core_vm_hostname, tenant_name, token)

        Report_file.add_line('Command ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        data_exists = False

        if 'securityGroups' in command_output:
            data_exists = True

        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            if data_exists:
                security_group_list = output['data']['securityGroups']

                for security_group in security_group_list:
                    name = security_group['name']
                    if security_group_name == name:
                        log.info('security group exists in ECM ')
                        return True

                log.info('security group does not exists in ECM')
                return False

            else:
                log.info('security group does not exists in ECM')
                return False

    except Exception as error:

        log.error('Error searching security_group in ECM %s', str(error))
        Report_file.add_line('Error searching security_group in ECM' + str(error))
        assert False


def create_node_security_group(node_name, create_file_name, transfer_file_name, security_group_name):
    try:
        log.info('start creating node security group for %s', node_name)
        Report_file.add_line('start creating node security group for ' + node_name)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        tenant_name = sit_data._SIT__tenantName

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/' + create_file_name,
            SIT.get_base_folder(SIT) + create_file_name,
        )
        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/' + transfer_file_name,
            SIT.get_base_folder(SIT) + transfer_file_name,
        )

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        sg_exists = check_security_group_exists_in_ecm(
            connection, token, core_vm_hostname, tenant_name, security_group_name
        )

        if sg_exists:
            log.info('Security group already exists in ECM , skipping creation of security group ')
            Report_file.add_line(
                'Security group already exists in ECM , skipping creation of security group '
            )
        else:
            command = '''curl --insecure "https://{}/ecm_service/securitygroups" -H "Accept: application/json" -H "AuthToken: {}" -H "Content-Type: application/json" --data @{}'''.format(
                core_vm_hostname, token, create_file_name)

            Report_file.add_line('command  ' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

            output = ast.literal_eval(command_out)
            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:

                security_group_id = output['data']['securityGroup']['id']
                log.info('Security group id %s', security_group_id)
                Report_file.add_line('Security group id  ' + security_group_id)

                log.info('start transfer node security group to VIM %s', node_name)

                command = '''curl --insecure "https://{}/ecm_service/securitygroups/{}/transfer" -H "Accept: application/json" -H "AuthToken: {}" -H "Content-Type: application/json" --data @{}'''.format(
                    core_vm_hostname, security_group_id, token, transfer_file_name)

                Report_file.add_line('command  ' + command)

                command_output = ExecuteCurlCommand.get_json_output(connection, command)
                command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

                output = ast.literal_eval(command_out)
                requestStatus = output['status']['reqStatus']

                if 'SUCCESS' in requestStatus:
                    order_id = output['data']['order']['id']

                    order_status, order_output = Common_utilities.orderReqStatus(
                        Common_utilities,
                        connection,
                        token,
                        core_vm_hostname,
                        order_id,
                        10,
                    )

                    if order_status:
                        log.info('Order Status is completed %s', order_id)
                        Report_file.add_line('Order Status is completed ' + order_id)

                    else:
                        log.info(order_output)
                        log.info('Order Status is failed with message mentioned above %s', order_id)
                        Report_file.add_line(
                            'Order Status is failed with message mentioned above ' + order_id)
                        assert False

            elif 'ERROR' in requestStatus:
                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for creating security group %s', command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command for creating security group ')
                assert False

    except Exception as error:
        log.error('Error creating node security group %s', str(error))
        Report_file.add_line('Error creating node security group' + str(error))
        assert False

    finally:
        connection.close()


def onboard_tosca_node_package(onboard_json_file, package_name, package_path, node_name):
    try:

        log.info('start onboarding package for %s', package_name)
        Report_file.add_line('start onboarding package for ' + package_name)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        tenant_name = sit_data._SIT__tenantName

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/' + onboard_json_file,
            SIT.get_base_folder(SIT) + onboard_json_file,
        )
        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_utilities/file_checksum.py',
            f'{SIT.get_base_folder(SIT)}file_checksum.py',
        )

        command = 'cp {}/{} /root/{}'.format(package_path, package_name, package_name)
        Report_file.add_line('package copy command: ' + command)

        stdin, stdout, stderr = connection.exec_command(command)

        command_error = str(stderr.read())
        if 'No such file or directory' in command_error:
            log.error('cannot copy package %s', command_error)
            Report_file.add_line('cannot copy package check the package path ' + command_error)
            assert False

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('curl command of generating package id ')
        command = '''curl --insecure 'https://{}/ecm_service/SOL005/vnfpkgm/v1/vnf_packages' -H 'AuthToken: {}' -H 'Accept: application/json' -H 'Content-Type: application/json' --data @{}'''.format(
            core_vm_hostname, token, onboard_json_file
        )

        Report_file.add_line('Curl command for generating package id ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('Fetching vnfPackage Id for OnBoarding')
        Report_file.add_line('Fetching vnfPackage Id for OnBoarding')
        output = ast.literal_eval(command_output[2:-1:1])

        vnfPackage_id = output['id']
        log.info('vnfPackage id is : %s', vnfPackage_id)
        log.info('package created successfully for %s', package_name)
        Report_file.add_line('Executed the curl command for creation of package : ' + vnfPackage_id)
        Report_file.add_line('Created package successfully')

        sit_data._SIT__vnf_packageId = vnfPackage_id

        if vnfPackage_id != '':
            log.info('Creating the curl commands of uploading the tosca package')
            command = '''split -d -b 20MB {}/{}  {}/chunk'''.format(package_path, package_name, package_path)
            stdin, stdout, stderr = connection.exec_command(command)

            log.info('waiting 50 sec to create all the chunks')
            time.sleep(50)

            command = 'ls -l {}/chunk*| wc -l'.format(package_path)
            Report_file.add_line('comamnd : ' + command)
            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('comamnd output : ' + command_output)
            TotalSplitedFileCount = int(command_output[2:-3])

            command = 'wc -c < {}/{}'.format(package_path, package_name)
            Report_file.add_line('comamnd : ' + command)
            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('comamnd output : ' + command_output)
            total_chunk_size = command_output[2:-3]
            command = 'python {}file_checksum.py {}/{}'.format(SIT.get_base_folder(SIT), package_path, package_name)
            Report_file.add_line('comamnd : ' + command)
            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('comamnd output : ' + command_output)
            file_checksum = command_output[2:-3]

            num = 0
            num1 = 0
            subs = 20000000
            while True:
                file_index = '%02d' % num
                if num != TotalSplitedFileCount:
                    file_name = 'chunk' + file_index
                    file_path = '{}/{}'.format(package_path, file_name)

                    command = 'wc -c < ' + file_path
                    Report_file.add_line('comamnd : ' + command)
                    stdin, stdout, stderr = connection.exec_command(command)
                    command_output = str(stdout.read())
                    Report_file.add_line('command output : ' + command_output)
                    splitedfilesizevalue = command_output[2:-3]

                    data = (
                            '"{\\"chunkSize\\":\\"'
                            + splitedfilesizevalue
                            + '\\",\\"fileChecksum\\":\\"'
                            + file_checksum
                            + '\\",\\"chunkData\\":\\"$(base64 '
                            + file_path
                            + ')\\"}"'
                    )

                    base_package = node_name + '_package_tosca.base64.req.body'
                    command = f'cd {SIT.get_base_folder(SIT)}; echo {data} > {base_package}'

                    log.info('command to create %s file %s', base_package, command)

                    connection.exec_command(command)

                    time.sleep(2)

                    range_low = num1

                    if int(total_chunk_size) - range_low < 20000000:
                        range_high = int(total_chunk_size) - 1
                    else:

                        range_high = subs - 1

                    command = '''curl --insecure -X PUT "https://{}:443/ecm_service/vnf_packages/{}/content" --header "AuthToken: {}" --header "Content-Range: bytes {}-{}/{}"  --header "tenantId:{}" --header "Content-Type: application/json" --data @{}'''.format(
                        core_vm_hostname,
                        vnfPackage_id,
                        token,
                        range_low,
                        range_high,
                        total_chunk_size,
                        tenant_name,
                        base_package,
                    )

                    Report_file.add_line('Curl command for upload ' + command)

                    command_output = ExecuteCurlCommand.get_json_output(connection, command)

                    Report_file.add_line('package upload creation curl output  ' + command_output)
                    output = ast.literal_eval(command_output[2:-1:1])
                    requestStatus = output['status']['reqStatus']

                    if 'SUCCESS' in requestStatus:

                        log.info('Successfully executed curl command')
                        Report_file.add_line('Successfully executed curl command')
                        Common_utilities.create_artifact_prop_file(Common_utilities,
                                                                   [vnfPackage_id], 'TOSCA_EPG_INSTALL')

                    elif 'ERROR' in requestStatus:

                        command_error = output['status']['msgs'][0]['msgText']

                        log.error('Error executing curl command for uploading package %s', command_error)
                        Report_file.add_line(command_error)
                        Report_file.add_line('Error executing curl command for uploading package')
                        assert False

                    num += 1
                    num1 += 20000000
                    subs += 20000000

                else:
                    break

        else:
            log.error('VNF-Package Id not found %s', vnfPackage_id)
            Report_file.add_line('VNF-Package Id not found ' + vnfPackage_id)
            assert False

    except Exception as error:
        log.error('Error onboarding TOSCA package %s', str(error))
        Report_file.add_line('Error onboarding TOSCA package ' + str(error))
        if vnfPackage_id != '':
            log.info('Failed Onboarding Doing Clean up of Tosca Package %s', vnfPackage_id)
            delete_tosca_vnf_package(vnfPackage_id, onboard_failed=True)
        assert False
    finally:
        connection.close()


def transfer_image_to_vim(node_name, file_name):
    try:
        log.info('Start transferring image to VIM  for %s', node_name)
        Report_file.add_line('Start transferring image to VIM  for ' + node_name)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/' + file_name,
            SIT.get_base_folder(SIT) + file_name,
        )

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = '''curl --insecure 'https://{}/ecm_service/images/{}/transfer' -H 'Accept: application/json' -H 'Content-Type: application/json' -H 'AuthToken: {}' --data @{}'''.format(
            core_vm_hostname, image_id, token, file_name
        )

        Report_file.add_line('command ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']

            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities, connection, token, core_vm_hostname, order_id, 10
            )

            if order_status:

                log.info('Order Status is completed %s', order_id)
                Report_file.add_line('Order Status is completed ' + order_id)

            else:

                log.info(order_output)
                log.info('Order Status is failed with message mentioned above %s', order_id)
                Report_file.add_line('Order Status is failed with message mentioned above ' + order_id)

                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for transferring image %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for transferring image ')
            assert False

    except Exception as error:

        log.error('Error transferring image for %s', node_name)
        Report_file.add_line('Error transferring image for ' + node_name)
        assert False

    finally:
        connection.close()


def fetch_net_subnet_ids_tosca_node(network_list):
    try:
        log.info('Start fetching net subnet ids for network list %s', str(network_list))
        Report_file.add_line('Start fetching net subnet ids for network list  ' + str(network_list))
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        rdb_vm_ip = ecm_host_data._Ecm_PI__RDB_VM_IP

        db_password = Common_utilities.fetch_cmdb_password(Common_utilities)

        log.info('connecting with database to fetch the data')

        conn = get_PSQL_connection(rdb_vm_ip, 'ecmdb1', 'cmdb', db_password)

        net_subnet_data = {}

        for network_name in network_list:
            network_id = get_record_id_from_PSQL_table(conn, 'cm_vn', 'id', 'name', network_name)

            subnet_id = get_record_id_from_PSQL_table(conn, 'cm_subnet', 'id', 'vn_id', network_id)

            net_subnet_data[network_name] = [network_id, subnet_id]

        log.info('Finished fetching net subnet ids for network list  ')
        Report_file.add_line('Finished fetching net subnet ids for network list  ')

        return net_subnet_data
    except Exception as error:

        log.error('Error fetching net subnet %s', str(error))
        Report_file.add_line('Error net subnet ' + str(error))
        assert False


def vm_vnfm_lcm_repo_directory():
    try:
        log.info('Start transferring vnflaf folder to pod /vnflcm-ext/current/vnf_package_repo path  ')
        Report_file.add_line(
            'Start transferring vnflaf folder to pod /vnflcm-ext/current/vnf_package_repo path'
        )

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        directory_server_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
        directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        if vm_vnfm_namespace == 'codeploy':

            file_path = 'id_rsa_tf.pem'

        else:

            file_path = 'eccd-2-3.pem'

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        nested_conn = ServerConnection.get_nested_server_connection(
            connection,
            ecm_server_ip,
            directory_server_ip,
            directory_server_username,
            file_path,
        )

        log.info('Removing old vnflaf package from vm vnfm')

        cmd = "rm -rf /vnflcm-ext/current/vnf_package_repo/vnflaf"
        command = get_vmvnfm_pod_cmd(cmd)

        nested_conn.exec_command(command)

        time.sleep(2)

        log.info('Transferring vnflaf folder to director server ip %s', directory_server_ip)

        ServerConnection.put_folder_scp(
            nested_conn,
            r'com_ericsson_do_auto_integration_files/vnflaf',
            r'/home/' + directory_server_username + '/',
        )
        pod_name = get_vmvnfm_pod()
        command = (
                'kubectl cp /home/' + directory_server_username + '/vnflaf'
                                                                  ' {}:/vnflcm-ext/current/vnf_package_repo/vnflaf'
                                                                  ' -n {}'.format(pod_name, vm_vnfm_namespace)
        )

        log.info('Transferring vnflaf folder to eric-vnflcm-service pod %s', command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        time.sleep(20)

        cmd = "chmod 777 -R /vnflcm-ext/current/vnf_package_repo/vnflaf"
        command = get_vmvnfm_pod_cmd(cmd)

        log.info('Giving 777 permission to vnflaf folder on eric-vnflcm-service pod %s', command)

        stdin, stdout, stderr = nested_conn.exec_command(command)
        time.sleep(2)

    except Exception as error:

        log.error('Error transferring vnflaf folder to pod /vnflcm-ext/current/vnf_package_repo path %s', str(error))
        Report_file.add_line(
            'Error transferring vnflaf folder to pod /vnflcm-ext/current/vnf_package_repo path ' + str(error))
        assert False

    finally:
        connection.close()


def create_nsd_package(packageName, filename):
    try:
        log.info('Start to create NSD package')
        Report_file.add_line('Start to create NSD package')
        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        remove_ecm_package_if_exists(packageName)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        update_nsd_create_package_file(filename, packageName)

        nsd_file_name = packageName + '.json'

        log.info('File name used to create nsd package %s ', nsd_file_name)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Transferring %s file to blade host server ', filename)
        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/' + filename,
            SIT.get_base_folder(SIT) + nsd_file_name,
        )
        time.sleep(2)

        log.info('Generating token to create NSD package')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        curl_command = '''curl --insecure "https://{}/ecm_service/SOL005/nsd/v1/ns_descriptors/" -H "Accept: application/json" -H "Content-Type: application/json" -H "AuthToken: {}" --data @{}'''.format(
            core_vm_hostname, token, nsd_file_name)

        output = Common_utilities.execute_curl_command(Common_utilities, connection, curl_command)

        if 'nsdOnboardingState' in str(output):

            if output['nsdOnboardingState'] == 'CREATED':

                global ns_descriptors_id
                ns_descriptors_id = output['id']
                Report_file.add_line('Create NSD package ns_descriptors_id - ' + ns_descriptors_id)
            else:

                Report_file.add_line('Error in Create NSD package')
                assert False

        else:
            log.error('ERROR in creating NSD package in EO-CM: %s', str(output))
            Report_file.add_line('ERROR in creating NSD package in EO-CM: ' + str(output))
            assert False

    except Exception as error:
        log.error('Error While creating NSD package %s', str(error))
        Report_file.add_line('Error while creating NSD package ' + str(error))
        assert False

    finally:
        connection.close()


def upload_nsd_package(pkgs_dir_path, package):
    try:
        log.info('Start to upload NSD package')
        Report_file.add_line('Start to upload NSD package')
        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        # if depl_type == 'CNF_NS_DEPL':
        #    curl_command = '''curl https://{}/ecm_service/SOL005/nsd/v1/ns_descriptors/{}/nsd_content -X 'PUT'  -H 'Content-Type: application/zip'  -H 'AuthToken: {}' --insecure -T '{}'.'''.format(core_vm_ip,ns_descriptors_id,token,package)
        #    command = ''+cd_cmd+';'+curl_command
        # else:
        curl_command = '''curl --insecure -i 'https://{}/ecm_service/SOL005/nsd/v1/ns_descriptors/{}/nsd_content' -X PUT -H 'Accept: */*' --compressed -H 'AuthToken: {}' -H 'Content-Type: application/zip' --data-binary @{}'''.format(
            core_vm_hostname, ns_descriptors_id, token, package
        )

        Report_file.add_line('Command : ' + curl_command)

        command_output = ExecuteCurlCommand.get_json_output(connection, curl_command, base_folder=pkgs_dir_path)

        output = command_output

        if '202 Accepted' in output:
            # time.sleep(60)
            # log.info('Successfully Uploaded the NSD package')

            check_nsd_upload_progress(ns_descriptors_id)

        else:

            Report_file.add_line('Error in Upload NSD package')
            assert False

    except Exception as error:
        log.error('Error While uploading NSD package %s', str(error))
        Report_file.add_line('Error while uploading NSd package ' + str(error))
        assert False
    finally:
        connection.close()


def check_nsd_upload_progress(nsd_package_id):
    try:

        log.info('Start to check NSD upload progress')
        Report_file.add_line('Start to check NSD upload progress')
        (
            ecm_server_ip,
            ecm_username,
            ecm_password,
        ) = Server_details.ecm_host_blade_details(Server_details)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        # Adding a polling time of 2 mins (120 sec)
        timeout = 120

        command = '''curl --insecure "https://{}/ecm_service/SOL005/nsd/v1/ns_descriptors/{}?$data="%"7B"%"22ericssonNfvoData"%"22"%"3Atrue"%"7D" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
            core_vm_hostname, nsd_package_id, token)

        created_in_output = 0

        while timeout != 0:

            output = Common_utilities.execute_curl_command(Common_utilities, connection, command)

            # converting output to string to check and see is
            # nsdOnboardingState in output. i.e str(output)
            if 'nsdOnboardingState' in str(output):

                nsdOnboardingState = output['nsdOnboardingState']

                if nsdOnboardingState == 'PROCESSING':
                    log.info('NSD upload is Ongoing. NSD_ONBOARDING_STATE: %s Waiting for 10sec to retry',
                             nsdOnboardingState)
                    Report_file.add_line(
                        'NSD upload is Ongoing. NSD_ONBOARDING_STATE: '
                        + nsdOnboardingState
                        + ' Waiting for 10sec to retry'
                    )
                    timeout = timeout - 10
                    time.sleep(10)
                elif nsdOnboardingState == 'ONBOARDED':
                    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
                    nsd_id = output['nsdId']
                    sit_data._SIT__nsd_id = nsd_id
                    SIT.set_nsd_id(SIT, nsd_id)
                    log.info('NSD ID is - %s', nsd_id)
                    log.info('NSD is uploaded successfully, nsdOnboardingState: %s', nsdOnboardingState)
                    Report_file.add_line(
                        'NSD is uploaded successfully, nsdOnboardingState: ' + nsdOnboardingState
                    )
                    break
                elif nsdOnboardingState == 'CREATED':
                    if created_in_output == 1:
                        log.error(
                            'NSD package onboarding state is still %s'
                            ' after 1 retry : %s',
                            nsdOnboardingState,
                            str(output)
                        )
                        Report_file.add_line(
                            'NSD package onboarding state is still '
                            + nsdOnboardingState
                            + ' after 1 retry : '
                            + str(output)
                        )
                        assert False

                    else:
                        log.info(
                            'NSD package onboarding is in CREATED state, nsdOnboardingState: %s'
                            ' Waiting for 10sec to retry',
                            nsdOnboardingState
                        )
                        Report_file.add_line(
                            'NSD package onboarding is in CREATED state, nsdOnboardingState: '
                            + nsdOnboardingState
                            + ' Waiting for 10sec to retry'
                        )
                        created_in_output += 1
                        timeout = timeout - 10
                        time.sleep(10)

                else:
                    log.error('NSD package onboarding state is %s', nsdOnboardingState)
                    Report_file.add_line('NSD package onboarding state is ' + nsdOnboardingState)
                    assert False

            else:
                log.error('ERROR with NSD Package onboard: %s', str(output))
                Report_file.add_line('ERROR with NSD Package onboard: ' + str(output))
                assert False

        if timeout == 0:
            log.info(
                'Automation script timed out after 2 minutes, NSD package onboarding state is %s',
                nsdOnboardingState
            )
            Report_file.add_line(
                'Automation script timed out after 2 minutes, NSD package onboarding state is '
                + nsdOnboardingState
            )
            assert False

    except Exception as error:
        log.error('Error while checking NSD upload progress %s', str(error))
        Report_file.add_line('Error while checking NSD upload progress ' + str(error))
        assert False

    finally:
        connection.close()


def fetch_nsd_details(connection, core_vm_hostname):
    try:
        log.info('Fetching the NSD details')
        Report_file.add_line('Fetching the NSD details')

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        command = '''curl --insecure "https://{}/ecm_service/SOL005/nsd/v1/ns_descriptors/{}" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
            core_vm_hostname, ns_descriptors_id, token)
        output = Common_utilities.execute_curl_command(Common_utilities, connection, command)
        nsd_id = output['nsdId']
        log.info('Fetching the NSD Details nsdId - ' + nsd_id)
        nsdName = output['nsdName']
        Report_file.add_line('Fetching the NSD Details nsName - ' + nsdName)
        return nsd_id, nsdName

    except Exception as error:
        log.error('Error While fetching NSD details %s', str(error))
        Report_file.add_line('Error while fetching NSD details ' + str(error))
        assert False


def update_cnf_ns_ecm(operation_type, file_name):
    """Update the NS with operatoion_type=Add_VNF/Remove_VNF to add and remove 1 instance of CNF-B and CNF-A."""
    log.info('Start to %s cnf from NS', operation_type)
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ns_instance_id = SIT.get_cnf_ns_instance_id(SIT)

        log.info('Transferring %s file to blade host server', file_name)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        curl_command = f'curl --insecure -i ' \
                       f'https://{core_vm_hostname}/ecm_service/SOL005/nslcm/v1/ns_instances/{ns_instance_id}/update ' \
                       f'-H "Content-Type: application/json" ' \
                       f'-H "AuthToken: {token}"' \
                       f' --data @{file_name}'

        output = ExecuteCurlCommand.get_json_output(connection, curl_command)

        if '202 Accepted' in output:

            order_id = re.findall('NS.*', output)[0].split('\\r\\n')[0].strip()
            log.info('Order id for %s is %s', operation_type, order_id)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 30)

            if order_status:
                log.info('Order Status is completed %s', order_id)
                log.info('CNF NS operation %s successful', operation_type)

            else:

                log.info('Order Status is failed with message mentioned above %s', order_id)
                assert False

        else:
            log.error('Error executing curl command, please check the logs for more details')
            assert False


    except Exception as e:
        log.error('Error While NS operation %s', str(e))
        assert False

    finally:
        connection.close()


def get_cnf_vapp_mgt_id(ns_instance_id, cnf_vapp_name):
    """Get the cnf vapp management system id ."""
    log.info('Start to get cnf vapp management system id')
    management_system_id = None
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        curl_command = f'curl --insecure ' \
                       f'"https://{core_vm_hostname}/ecm_service/vapps?$filter=networkServiceId%3D%27{ns_instance_id}%27"' \
                       f' -H "AuthToken: {token}"'
        output = Common_utilities.execute_curl_command(Common_utilities, connection, curl_command)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            for cnf in output['data']['vapps']:
                cnf_name = cnf['name']
                if cnf_vapp_name in cnf_name:
                    management_system_id = cnf['managementSystemId']
                    log.info('management system id %s', management_system_id)

            return management_system_id

        elif 'ERROR' in requestStatus:
            log.error('Error executing curl command for getting cnf vapp management system id')
            assert False

    except Exception as e:
        log.error('Error While getting cnf vapp management system id %s', str(e))
        assert False
    finally:
        if connection:
            connection.close()


def scale_cnf_ns_ecm(operation_type, file_name):
    """Scale the NS CNF vapp with operation_type=SCALE_OUT/SCALE_OUT on CNF-A2"""
    log.info('Start to %s cnf vapp from NS', operation_type)
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ns_instance_id = SIT.get_cnf_ns_instance_id(SIT)

        log.info('Transferring %s file to blade host server', file_name)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        curl_command = f'curl --insecure -i ' \
                       f'https://{core_vm_hostname}/ecm_service/SOL005/nslcm/v1/ns_instances/{ns_instance_id}/scale ' \
                       f'-H "Content-Type: application/json" ' \
                       f'-H "AuthToken: {token}"' \
                       f' --data @{file_name}'

        output = ExecuteCurlCommand.get_json_output(connection, curl_command)

        if '202 Accepted' in output:

            order_id = re.findall('NS.*', output)[0].split('\\r\\n')[0].strip()
            log.info('Order id for %s is %s', operation_type, order_id)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 30)

            if order_status:
                log.info('Order Status is completed %s', order_id)
                log.info('CNF NS operation %s successful', operation_type)

            else:

                log.info('Order Status is failed with message mentioned above %s', order_id)
                assert False

        else:
            log.error('Error executing curl command, please check the logs for more details')
            assert False


    except Exception as e:
        log.error('Error While NS operation %s', str(e))
        assert False

    finally:
        if connection:
            connection.close()


def create_ns_ecm(node_name, update_attr_key):
    """
    Create network service in ECM , method can be used for any node service
    """
    log.info('Start to create NS for %s', node_name)
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        service_name = Common_utilities.get_name_with_random_plaintext(Common_utilities, f'{node_name}-service')
        SIT.set_ecm_ns_name(SIT, service_name)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        service_file = 'createNS.json'
        nsdId, nsdName = fetch_nsd_details(connection, core_vm_hostname)

        update_ns_create_package_file(service_file, nsdId, service_name)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + service_file,
                                       SIT.get_base_folder(SIT) + service_file)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        curl_command = f'curl --insecure https://{core_vm_hostname}/ecm_service/SOL005/nslcm/v1/ns_instances -H ' \
                       f'"Content-Type: application/json" -H "AuthToken: {token}" --data @{service_file} '

        output = Common_utilities.execute_curl_command(Common_utilities, connection, curl_command)
        if 'Error' in output or 'Failure' in output or 'Invalid' in output:
            log.error("Error while creating network service in EOCM")
            assert False

        global ns_instances_id
        ns_instances_id = output['id']
        log.info('Created network service instances id - %s', ns_instances_id)
        update_runtime_env_file(update_attr_key, ns_instances_id)

    except Exception as e:
        log.error('Error While creating network service in EOCM %s ', str(e))
        assert False
    finally:
        if connection:
            connection.close()


def instantiate_ns_ecm(node_name, file_name):
    """
    Instantiate network service in ECM , method can be used for any node service
    """
    log.info('Start to instantiate network service for %s', node_name)
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        curl_command = f'curl --insecure -i -X POST "https://{core_vm_hostname}/ecm_service/SOL005/nslcm/v1' \
                       f'/ns_instances/{ns_instances_id}/instantiate" -H "AuthToken: {token}" -H "Content-Type: ' \
                       f'application/json" --data @{file_name}'

        command_output = ExecuteCurlCommand.get_json_output(connection, curl_command)

        if '202 Accepted' in command_output:
            order_id = re.findall('NS.*', command_output)[0].split('\\r\\n')[0].strip()
            log.info('Instantiate NS Order Id - %s', order_id)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
            order_status, order_output = Common_utilities.NSorderReqStatus(Common_utilities, connection,
                                                                           token, core_vm_hostname, order_id,
                                                                           30)
            if order_status:
                log.info("Successfully Completed Instantiation of NS")
            else:
                log.error('order status for NS Instantiate has been failed  %s', order_id)
                assert False

        else:
            Report_file.add_line('Error in While doing Instantiation of NS')
            assert False

    except Exception as e:
        log.error('Error While doing Instantiate NS %s', str(e))
        assert False

    finally:
        if connection:
            connection.close()
