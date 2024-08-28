'''
Created on jul 17, 2020

@author: zsyapra
'''

import base64
import ast
import time
from paramiko import sftp_client
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.file_utils import set_value_in_property_file, replace
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.LPIS_files_update import update_register_vm_vnfm
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_runtime_env_file
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_testhotel_vmvnfm_host_connection, \
    get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_scripts.PROJ_VIM import get_classic_ecm_version
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.EPIS import EPIS

log = Logger.get_logger('CNFNS_INSTANTIATION_PRE_REQ.py')


def back_up_of_baseenv_file():
    try:
        log.info('Logging to ABCD VM Server and taking backup of file according to platform')
        Report_file.add_line('Logging to ABCD VM Server and taking backup of file according to platform')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        abcd_vm_serverip, abcd_username, abcd_password = Server_details.get_abcd_vm_details(Server_details)
        platform = Server_details.get_environment_user_platform(Server_details)
        deployment_type = Server_details.get_deployment_type(Server_details)
        if deployment_type == 'HA':
            filename = 'baseenv.HA'
        else:
            filename = 'baseenv.nonHA'
        source_file_abs_path = '/ecm-umi/install/' + platform + '/'
        dest_file_abs_path = '/ecm-umi/install/' + platform + '/'
        global back_up_file_name
        back_up_file_name = Common_utilities.get_name_with_timestamp(Common_utilities, filename)
        connection = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username,
                                                                    ecm_password, abcd_vm_serverip,
                                                                    abcd_username,
                                                                    abcd_password)
        Common_utilities.take_back_up_of_a_file(Common_utilities, connection, filename, back_up_file_name,
                                                source_file_abs_path, dest_file_abs_path)
        connection.close()



    except Exception as e:
        log.error('Error while taking backup of platform file ' + str(e))
        Report_file.add_line('Error while taking backup of platform file ' + str(e))
        assert False


def parserdict_and_update_file(connection, dict):
    file_name = r'com_ericsson_do_auto_integration_files/baseenv.ini'
    try:
        for key in dict:
            command = dict[key]
            # SM-134842
            if 'HELM_REGISTRY_REPO' == key:
                value = command
            else:
                stdin, stdout, stderr = connection.exec_command(command)
                command_output = str(stdout.read())[2:-3:]
                Report_file.add_line('executed ' + command + ' output' + command_output)
                value = command_output
                if value == '':
                    log.error(f'Error while executing {command}')
                    Report_file.add_line(f'Error while executing {command}')
                    assert False
                if key == 'HELM_REGISTRY_ADDRESS':
                    get_full_FQDN = value.split('https://')[1]
                    value = get_full_FQDN

            set_value_in_property_file(file_name, key, value)

    except Exception as e:
        log.error('Failed while parsing details %s', str(e))
        Report_file.add_line('Failed while parsing details %s', str(e))
        assert False

    # This Function will earse the content in a file


def erase_the_content_of_a_file(filename):
    file_path = 'com_ericsson_do_auto_integration_files/' + filename
    with open(file_path, 'w'): pass


def retrieve_helm_repo_details(app=False):
    try:
        log.info('Retrieving HELM repo username, password and URL from the E-VNFM')
        Report_file.add_line('Retrieving HELM repo username, password and URL from the E-VNFM')
        filename = 'baseenv.ini'
        # Erasing the content of a file, before starting to update the new option values in a file
        erase_the_content_of_a_file(filename)
        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        helm_registry_username_cmd = 'kubectl get secrets eric-lcm-helm-chart-registry -o jsonpath=\'{.data.BASIC_AUTH_USER}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        helm_registry_passwd_cmd = 'kubectl get secrets eric-lcm-helm-chart-registry -o jsonpath=\'{.data.BASIC_AUTH_PASS}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        helm_registry_host_cmd = 'kubectl get secrets eric-lcm-helm-chart-registry -o jsonpath=\'{.data.url}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        dict = {'HELM_REGISTRY_USERNAME': helm_registry_username_cmd,
                'HELM_REGISTRY_PASSWORD': helm_registry_passwd_cmd,
                'HELM_REGISTRY_ADDRESS': helm_registry_host_cmd, 'HELM_REGISTRY_REPO': 'onboarded'}
        if app == 'TEST-HOTEL':
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_director_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
            vm_vnfm_director_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
            director_connection = get_testhotel_vmvnfm_host_connection(vm_vnfm_director_ip,
                                                                       vm_vnfm_director_username)
        else:
            director_connection = get_VMVNFM_host_connection()

        parserdict_and_update_file(director_connection, dict)



    except Exception as e:
        log.error('Error while retrieving HELM repo details %s', str(e))
        Report_file.add_line('Error while retrieving HELM repo details %s', str(e))
        assert False

    finally:
        director_connection.close()


def retrieve_helm_repo_details_cn():
    director_connection = None
    try:
        Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        eocm_namespace = Ecm_core.get_ecm_namespace(Ecm_core)
        log.info('Retrieving HELM repo username, password and URL from the E-VNFM')
        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        secret_name = 'eric-eo-cm-onboarding-helm-repo-credentials'
        configmap_name = 'eric-eo-cm-onboarding-helm-repo-url'
        username_parameter = 'user'
        password_parameter = 'password'
        helm_details_dict = {}

        helm_registry_username_cmd = 'kubectl get secrets eric-lcm-helm-chart-registry -o jsonpath=\'{.data.BASIC_AUTH_USER}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        helm_registry_passwd_cmd = 'kubectl get secrets eric-lcm-helm-chart-registry -o jsonpath=\'{.data.BASIC_AUTH_PASS}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        helm_registry_host_cmd = 'kubectl get secrets eric-lcm-helm-chart-registry -o jsonpath=\'{.data.url}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'

        dict = {'HELM_REGISTRY_USERNAME': helm_registry_username_cmd,
                'HELM_REGISTRY_PASSWORD': helm_registry_passwd_cmd,
                'HELM_REGISTRY_ADDRESS': helm_registry_host_cmd}
        director_connection = get_VMVNFM_host_connection()
        for cmd in dict.keys():
            if cmd == 'HELM_REGISTRY_ADDRESS':
                stdin, stdout, stderr = director_connection.exec_command(dict[cmd])
                command_output = str(stdout.read())[2:-3:]
                log.info('executed %s got output: %s', dict[cmd], command_output)
                helm_fqdn = command_output.split('//')[1]
                helm_details_dict['HELM_REGISTORY_ADDRESS_FQDN'] = helm_fqdn
            else:
                stdin, stdout, stderr = director_connection.exec_command(dict[cmd])
                command_output = str(stdout.read())[2:-3:]
                log.info('executed %s got output: %s', dict[cmd], command_output)
                auth_basic = base64.b64encode(bytes(command_output, encoding='utf-8'))
                decoded_auth_basic = auth_basic.decode('utf-8')
                log.info(decoded_auth_basic)
                helm_details_dict[str(cmd) + '_ENCRYPTED_VALUE'] = decoded_auth_basic

        log.info('Encrypted values: {}'.format(helm_details_dict))
        log.info('updating helm username and password in secret: %s', secret_name)

        update_secret(director_connection, secret_name, username_parameter, eocm_namespace,
                      helm_details_dict['HELM_REGISTRY_USERNAME_ENCRYPTED_VALUE'])
        update_secret(director_connection, secret_name, password_parameter, eocm_namespace,
                      helm_details_dict['HELM_REGISTRY_PASSWORD_ENCRYPTED_VALUE'])
        log.info('Updating configmap: %s with url: %s', configmap_name, helm_details_dict[
            'HELM_REGISTORY_ADDRESS_FQDN'])
        new_value = 'host: https://' + helm_details_dict['HELM_REGISTORY_ADDRESS_FQDN']
        value_to_update_in_configmap = 'host:*'
        update_configmap(director_connection, configmap_name, eocm_namespace, value_to_update_in_configmap,
                         new_value)

    except Exception as e:
        log.error('Error while updating HELM repo details %s', str(e))
        assert False

    finally:
        director_connection.close()


def retrieve_helm_registry_certificate():
    connection = None
    try:
        eocm_namespace = Ecm_core.get_ecm_namespace(Ecm_core)
        cn_env_name = EPIS.get_cn_env_name(EPIS)
        tls_cert_file = f'com_ericsson_do_auto_integration_files/EricssonCerts/{cn_env_name}_helm.cer'
        log.info('Using helm tls certificate from filepath: %s', tls_cert_file)
        log.info('Encrypting the helm tls certificate')
        with open(tls_cert_file, 'r') as helm_cert:
            helm_cert_content = helm_cert.read()
        auth_basic = base64.b64encode(bytes(helm_cert_content, encoding='utf-8'))
        decoded_auth_basic = auth_basic.decode('utf-8')
        log.info('Helm certificate encrypted value: %s', decoded_auth_basic)
        helm_secret_param = 'helm-repo.crt'
        helm_secret_name = 'eric-eo-cm-onboarding-helm-repo-tls'
        connection = get_VMVNFM_host_connection()
        update_secret(connection, helm_secret_name, helm_secret_param, eocm_namespace, decoded_auth_basic)
        log.info('Helm certificate have been successfully updated')
    except Exception as e:
        log.error('helm certificate update failed')
        assert False
    finally:
        connection.close()


def update_secret(connection, secret_name, parameter, eocm_namespace, value):
    try:
        log.info('Updating %s with value: %s in secret: %s', parameter, value, secret_name)
        secret_update_cmd = '''kubectl patch secrets {} -n {} --type='json' -p='[{{'op' : 'replace' , 'path' : '/data/{}' , 'value' : {}}}]' '''.format(
            secret_name, eocm_namespace, parameter, value)
        log.info('Secret update command: %s', secret_update_cmd)

        stdin, stdout, stderr = connection.exec_command(secret_update_cmd)
        command_output = str(stdout.read())
        command_output_err = str(stderr.read())
        log.info('Secret update command output: %s', command_output)

        if f'{secret_name} patched' in command_output:
            log.info('Secret has been updated successfully')
        else:
            log.error('Secret failed to update')
            log.error('Error occured: %s', command_output_err)
            assert False

    except Exception as e:
        log.error('Could not update secret due to exception: %s', str(e))
        assert False


def update_configmap(connection, configmap_name, eocm_namespace, value_to_replace, new_value):
    try:
        log.info('Updating host with value: %s in configmap: %s', new_value, configmap_name)
        configmap_update_cmd = '''kubectl get configmap {} -n {} -o yaml| sed -e 's|{} .*|{}|' | kubectl apply -f -'''.format(
            configmap_name, eocm_namespace, value_to_replace, new_value)
        log.info('Configmap update command: %s', configmap_update_cmd)
        stdin, stdout, stderr = connection.exec_command(configmap_update_cmd)
        command_output = str(stdout.read())
        command_output_err = str(stderr.read())
        log.info('Configmap update command output: %s', command_output)
        if f'{configmap_name} configured' in command_output:
            log.info('Configmap has been updated successfully')
        else:
            log.info('Configmap failed to update')
            log.error('Error occured: %s', command_output_err)
            assert False

    except Exception as e:
        log.error('Could not update configmap due to exception: %s', str(e))
        assert False


def retrieve_docker_registry_details(app=False):
    try:
        log.info('Retrieving Docker registry username, password and URL from the E-VNFM')
        Report_file.add_line('Retrieving  Docker registry username, password and URL from the E-VNFM')
        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        docker_registry_username_cmd = 'kubectl get secrets eric-evnfm-rbac-default-user -o jsonpath=\'{.data.userid}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        docker_registry_passwd_cmd = 'kubectl get secrets eric-evnfm-rbac-default-user -o jsonpath=\'{.data.userpasswd}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        docker_registry_host_cmd = 'kubectl get secrets eric-lcm-container-registry-registry -o jsonpath=\'{.data.url}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        dict = {'DOCKER_REGISTRY_USERNAME': docker_registry_username_cmd,
                'DOCKER_REGISTRY_PASSWORD': docker_registry_passwd_cmd,
                'DOCKER_REGISTRY_ADDRESS': docker_registry_host_cmd}
        if app == 'TEST-HOTEL':
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_director_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
            vm_vnfm_director_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
            director_connection = get_testhotel_vmvnfm_host_connection(vm_vnfm_director_ip,
                                                                       vm_vnfm_director_username)
        else:
            director_connection = get_VMVNFM_host_connection()
        parserdict_and_update_file(director_connection, dict)

    except Exception as e:
        log.error('Error while retrieving Docker registry details %s', str(e))
        assert False

    finally:
        director_connection.close()


def retrieve_docker_registry_details_cn():
    director_connection = None
    try:
        Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        eocm_namespace = Ecm_core.get_ecm_namespace(Ecm_core)
        log.info('Retrieving Docker registry username, password and URL from the E-VNFM')
        secret_name = 'eric-eo-cm-onboarding-docker-registry-credentials'
        configmap_name = 'eric-eo-cm-onboarding-docker-registry-url'
        username_parameter = 'user'
        password_parameter = 'password'
        docker_details_dict = {}
        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        docker_registry_username_cmd = 'kubectl get secrets eric-evnfm-rbac-default-user -o jsonpath=\'{.data.userid}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        docker_registry_passwd_cmd = 'kubectl get secrets eric-evnfm-rbac-default-user -o jsonpath=\'{.data.userpasswd}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        docker_registry_host_cmd = 'kubectl get secrets eric-lcm-container-registry-registry -o jsonpath=\'{.data.url}\' -n ' + vm_vnfm_namespace + ' | base64 -d; echo'
        dict = {'DOCKER_REGISTRY_USERNAME': docker_registry_username_cmd,
                'DOCKER_REGISTRY_PASSWORD': docker_registry_passwd_cmd,
                'DOCKER_REGISTRY_ADDRESS': docker_registry_host_cmd}
        director_connection = get_VMVNFM_host_connection()
        for cmd in dict.keys():
            if cmd == 'DOCKER_REGISTRY_ADDRESS':
                stdin, stdout, stderr = director_connection.exec_command(dict[cmd])
                command_output = str(stdout.read())[2:-3:]
                log.info('Executed %s got output: %s', dict[cmd], command_output)
                docker_fqdn = command_output
                docker_details_dict['DOCKER_REGISTRY_ADDRESS_FQDN'] = docker_fqdn
            else:
                stdin, stdout, stderr = director_connection.exec_command(dict[cmd])
                command_output = str(stdout.read())[2:-3:]
                log.info('Executed %s got output: %s', dict[cmd], command_output)
                auth_basic = base64.b64encode(bytes(command_output, encoding='utf-8'))
                decoded_auth_basic = auth_basic.decode('utf-8')
                log.info(decoded_auth_basic)
                docker_details_dict[str(cmd) + '_ENCRYPTED_VALUE'] = decoded_auth_basic

        log.info('Encrypted values: %s', docker_details_dict)
        log.info('updating docker registory username and password in secret: %s', secret_name)

        update_secret(director_connection, secret_name, username_parameter, eocm_namespace,
                      docker_details_dict['DOCKER_REGISTRY_USERNAME_ENCRYPTED_VALUE'])
        update_secret(director_connection, secret_name, password_parameter, eocm_namespace,
                      docker_details_dict['DOCKER_REGISTRY_PASSWORD_ENCRYPTED_VALUE'])
        log.info('Updating configmap: %s with url: %s', configmap_name,
                 docker_details_dict['DOCKER_REGISTRY_ADDRESS_FQDN'])
        new_value = 'host: ' + docker_details_dict['DOCKER_REGISTRY_ADDRESS_FQDN']
        value_to_update_in_configmap = 'host:*'
        update_configmap(director_connection, configmap_name, eocm_namespace, value_to_update_in_configmap,
                         new_value)
    except Exception as e:
        log.error('Error while updating docker registory details %s', str(e))
        assert False

    finally:
        director_connection.close()


def retrieve_docker_registry_certificate(app=False):
    try:

        log.info('Retrieve a docker registry certificate')
        Report_file.add_line('Retrieve a docker registry certificate')
        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        file_name = 'tls.crt'
        docker_registry_cert_cmd = 'kubectl get secret registry-tls-secret -o jsonpath=\'{.data.tls\.crt}\' -n ' + vm_vnfm_namespace + ' | base64 -d >>' + file_name
        if app == 'TEST-HOTEL':
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_director_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
            vm_vnfm_director_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
            connection = get_testhotel_vmvnfm_host_connection(vm_vnfm_director_ip, vm_vnfm_director_username)
        else:
            connection = get_VMVNFM_host_connection()
        remove_command = 'rm -rf ' + file_name
        stdin, stdout, stderr = connection.exec_command(remove_command)
        command_output = str(stdout.read())
        stdin, stdout, stderr = connection.exec_command(docker_registry_cert_cmd)
        command_output = str(stdout.read())
        Report_file.add_line('executed ' + docker_registry_cert_cmd + ' output' + command_output)
        filename = 'tls'
        # command = 'mv '+file_name+' '+filename
        # stdin, stdout, stderr = connection.exec_command(docker_registry_cert_cmd)
        command_output = str(stdout.read())
        platform = Server_details.get_environment_user_platform(Server_details)
        absolute_filepath = '/ecm-umi/install/' + platform + '/stage/cert/registry/tls'
        abcd_vm_serverip, abcd_username, abcd_password = Server_details.get_abcd_vm_details(Server_details)

        source_filepath = file_name
        destination_filepath = absolute_filepath
        # Server_connection.transfer_files_using_scp(Server_connection, connection, abcd_vm_serverip, abcd_username, abcd_password, absolute_filepath, file_name)
        ServerConnection.transfer_files_with_user_and_passwd(connection, abcd_username,
                                                             abcd_password, source_filepath, abcd_vm_serverip,
                                                             destination_filepath)


    except Exception as e:
        log.error('Error while retrieving Docker registry certificate ' + str(e))
        Report_file.add_line('Error while retrieving Docker registry certificate ' + str(e))
        assert False

    finally:
        connection.close()


def retrieve_docker_registry_certificate_cn():
    connection = None
    try:
        Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        eocm_namespace = Ecm_core.get_ecm_namespace(Ecm_core)
        secret_name = 'eric-eo-cm-onboarding-docker-registry-tls'
        docker_crt_parameter = 'docker-registry.crt'
        log.info('Retrieve a docker registry certificate')

        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        connection = get_VMVNFM_host_connection()
        docker_registry_cert_cmd = 'kubectl get secret registry-tls-secret -o jsonpath=\'{.data.tls\.crt}\' -n ' + vm_vnfm_namespace + ' | base64 -d > docker_reg_crt'
        log.info('Command to retrieve docker registry certificate: %s', docker_registry_cert_cmd)
        stdin, stdout, stderr = connection.exec_command(docker_registry_cert_cmd)
        command_output = str(stdout.read())
        log.info('Docker registry certificate: %s', command_output)

        docker_crt_file_path = f'/home/{Ecm_core.get_vm_vnfm_director_username(Ecm_core)}/docker_reg_crt'
        docker_crt_file = 'docker_reg_crt'

        log.info('fetching docker cert file to get encoded certificate ')
        ServerConnection.get_file_sftp(connection, docker_crt_file_path, 'docker_reg_crt')
        with open(docker_crt_file, 'r') as docker_reg_cert:
            docker_cert_content = docker_reg_cert.read()
        auth_basic = base64.b64encode(bytes(docker_cert_content, encoding='utf-8'))
        decoded_auth_basic = auth_basic.decode('utf-8')
        log.info('Docker certificate encrypted value: %s', decoded_auth_basic)
        update_secret(connection, secret_name, docker_crt_parameter, eocm_namespace, decoded_auth_basic)
        log.info('Docker registry certificate has been updated successfully')
    except Exception as e:
        log.error('Error while retrieving and updating Docker registry certificate %s', str(e))
        assert False

    finally:
        connection.close()


def update_baseenv_file():
    try:
        log.info('Start to update theoption values in baseenv file')
        Report_file.add_line('Start to update theoption values in baseenv file')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        abcd_vm_serverip, abcd_username, abcd_password = Server_details.get_abcd_vm_details(Server_details)
        platform = Server_details.get_environment_user_platform(Server_details)
        deployment_type = Server_details.get_deployment_type(Server_details)
        if deployment_type == 'HA':
            filename = 'baseenv.HA'
        else:
            filename = 'baseenv.nonHA'
        baseenv_filename = 'baseenv.ini'
        abs_path = '/ecm-umi/install/' + platform + '/'
        updated_baseenv_file_fullpath = abs_path + baseenv_filename
        baseenv_file_fullpath = abs_path + filename

        connection = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username,
                                                                    ecm_password, abcd_vm_serverip,
                                                                    abcd_username,
                                                                    abcd_password)
        ServerConnection.put_file_sftp(connection,
                                       r'com_ericsson_do_auto_integration_files/' + baseenv_filename,
                                       updated_baseenv_file_fullpath)

        sftp = connection.open_sftp()
        sftp.get(baseenv_file_fullpath, filename)
        sftp.get(updated_baseenv_file_fullpath, "baseenv.ini")
        sftp.close()

        baseenv_file_name = filename
        updval_filename = "baseenv.ini"
        reading_baseenv_file = open(baseenv_file_name, "r")
        reading_lines = reading_baseenv_file.readlines()
        reading_baseenv_file.close()
        reading_updval_file = open(updval_filename, "r")
        read_updval_lines = reading_updval_file.readlines()
        reading_updval_file.close()
        for line in read_updval_lines:
            if line == '\n' or line == '':
                pass
            key = line.split("=")[0]

            for line1 in reading_lines:

                if key in line1:
                    pattern = line1
                    subst = line
                    replace(baseenv_file_name, pattern, subst)

        connection = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username,
                                                                    ecm_password, abcd_vm_serverip,
                                                                    abcd_username,
                                                                    abcd_password)
        # Server_connection.put_file_sftp(Server_connection,connection,r'com_ericsson_do_auto_integration_files/'+baseenv_filename, updated_baseenv_file_fullpath)
        sftp = connection.open_sftp()
        sftp.put(baseenv_file_name, baseenv_file_fullpath)
        sftp.put(updval_filename, updated_baseenv_file_fullpath)
        sftp.close()

    except Exception as e:
        log.error('Error updating ' + baseenv_file_fullpath + ' file ' + str(e))
        Report_file.add_line('Error while updating ' + baseenv_file_fullpath + ' file' + str(e))
        assert False

    finally:
        connection.close()


def configure_helm_and_docker_registry_service():
    try:
        log.info('Start to install ecm')
        Report_file.add_line('Start to install ecm')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        abcd_vm_serverip, abcd_username, abcd_password = Server_details.get_abcd_vm_details(Server_details)
        platform = Server_details.get_environment_user_platform(Server_details)
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
        deployment_type = Server_details.get_deployment_type(Server_details)

        if deployment_type == 'HA':
            filename = 'ecmInstall_HA.sh'
        else:
            filename = 'ecm_install_nonHA.sh'
        if platform == 'kvm':
            old_version = '20.7.0.0.2115.2317'
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            ecm_verison = get_classic_ecm_version(connection, core_vm_ip, old_version)
            if ecm_verison == True:
                option = '6b'
            else:
                option = '6a'
            connection.close()

        elif platform == 'eoo' and deployment_type == 'HA':
            option = '4da'
        else:
            option = '3bd'
        abs_path = '/ecm-umi/install/' + platform

        connection = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username,
                                                                    ecm_password, abcd_vm_serverip,
                                                                    abcd_username,
                                                                    abcd_password)

        command = 'cd ' + abs_path + ' ; ./' + filename + ' -anp' + option

        Report_file.add_line('Command : ' + command)
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())
        Report_file.add_line('Command output : ' + command_output)
        log.info(command_output)

        if 'failed=0' in command_output:
            log.info("Successfully configured Docker and HELM Registry....")
        else:
            log.error(
                "Failed to configured Docker and HELM Registry - please check command output for details" + command_output)
            assert False

    except Exception as e:
        log.error('Error while configuring Docker and HEKM registry ' + filename + '' + str(e))
        Report_file.add_line('Error while configuring Docker and HEKM registry ' + filename + '' + str(e))
        assert False


def update_the_file(sftp_client, output_filepath):
    with sftp_client.open(output_filepath, 'r') as upd_file:
        lines = upd_file.readlines()
        with sftp_client.open(output_filepath, "w") as sources:
            for line in lines:
                if line == '\n':
                    pass
                else:
                    val = line.split('=')[1]
                    value = val.split('\n')[0]
                    key = line.split('=')[0]
                    replaced_key = key.replace('.', '_')

                    if "user_name" in replaced_key:
                        replaced_key = replaced_key.replace('user_name', 'username')
                    elif "user_password" in replaced_key:
                        replaced_key = replaced_key.replace('user_password', 'password')
                    elif "host" in replaced_key:
                        replaced_key = replaced_key.replace('host', 'address')
                    else:
                        pass
                    import re
                    replaced_key = replaced_key.upper()
                    sources.write(re.sub(key, replaced_key, line))


def verify_updated_baseenv_file():
    try:
        log.info('Start to verify the updated values after EO-CM service configured')
        Report_file.add_line('Start to verify the updated values after EO-CM service configured')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip, core_vm_username, core_vm_password = Server_details.core_vm_details(Server_details,
                                                                                        'core_vm_ip')
        abcd_vm_serverip, abcd_username, abcd_password = Server_details.get_abcd_vm_details(Server_details)
        platform = Server_details.get_environment_user_platform(Server_details)
        deployment_type = Server_details.get_deployment_type(Server_details)

        if deployment_type == 'HA':
            filename = 'baseenv.HA'
        else:
            filename = 'baseenv.nonHA'
        updated_baseenv_filename = 'baseenv.ini'
        abs_filepath = '/ecm-umi/install/' + platform + '/'
        file_path = '/ecm-umi/install/' + platform + '/' + filename
        redirect_cmd_output_filename = 'output.txt'
        output_filepath = '/ecm-umi/install/' + platform + '/' + redirect_cmd_output_filename

        connection = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username,
                                                                    ecm_password, core_vm_ip,
                                                                    core_vm_username,
                                                                    core_vm_password)

        cmd = "cat /usr/lib/systemd/system/onboarding-docker.service | grep -i '[\._]registry[\._]' | awk '{print $2}'>>" + redirect_cmd_output_filename
        stdin, stdout, stderr = connection.exec_command(cmd)
        command_output = str(stdout.read())

        source_filepath = redirect_cmd_output_filename
        destination_filepath = abs_filepath
        ServerConnection.transfer_files_with_user_and_passwd(connection, abcd_username,
                                                             abcd_password, source_filepath, abcd_vm_serverip,
                                                             destination_filepath)

        # Server_connection.transfer_files_using_scp(Server_connection, connection, abcd_vm_serverip, abcd_username, abcd_password, abs_filepath, redirect_cmd_output_filename)
        rm_cmd = 'rm -rf ' + redirect_cmd_output_filename

        stdin, stdout, stderr = connection.exec_command(rm_cmd)
        command_output = str(stdout.read())
        connection.close()

        comp_list = ['HELM_REGISTRY_USERNAME', 'HELM_REGISTRY_PASSWORD', 'HELM_REGISTRY_ADDRESS', 'HELM_REGISTRY_REPO',
                     'DOCKER_REGISTRY_USERNAME', 'DOCKER_REGISTRY_PASSWORD', 'DOCKER_REGISTRY_ADDRESS']

        abcd_connection = ServerConnection.make_nested_server_connection(ecm_server_ip,
                                                                         ecm_username, ecm_password,
                                                                         abcd_vm_serverip,
                                                                         abcd_username, abcd_password)
        sftp_client = abcd_connection.open_sftp()

        some_list = []
        update_the_file(sftp_client, output_filepath)
        with sftp_client.open(file_path, 'r') as org_file:
            lines = org_file.readlines()
            with sftp_client.open(output_filepath, 'r') as upd_file:
                for line in upd_file:
                    if line == '\n':
                        pass
                    else:
                        val = line.split('=')[1]
                        value = val.split('\n')[0]

                        key = line.split('=')[0]

                    # replaced_key = key
                    if key in comp_list:
                        for pattern in lines:
                            if key in pattern:

                                orgi_value = pattern.split('=')[1]
                                org_value = orgi_value.split('\n')[0]
                                org_value = org_value.strip('\r')

                                # SM-134842
                                # to get this matched with baseenv.HA file
                                if key == "HELM_REGISTRY_ADDRESS":
                                    org_value = "https://" + org_value + ":443"

                                if value.strip("'") == org_value:
                                    log.info("Matched options - " + key)
                                    Report_file.add_line("Matched options - " + key)
                                else:
                                    log.info('Unmatched options Key - ' + key)
                                    log.info(
                                        "Unmatched option Key value  from baseenv.HA file - " + org_value)
                                    log.info("Unmatched option Key value from updated file - " + value)
                                    Report_file.add_line('Unmatched options are - ' + key)
                                    Report_file.add_line(
                                        "Unmatched option Key value  from baseenv.HA file - " + org_value)
                                    Report_file.add_line(
                                        "Unmatched option Key value from updated file - " + value)
                                    some_list.append(key)

                        if len(some_list) != 0:
                            log.info("Option Values are not same")
                            Report_file.add_line('Option values are not same ')
                            assert False

        sftp_client.remove('/ecm-umi/install/' + platform + '/' + redirect_cmd_output_filename)

    except Exception as e:
        log.error('Error while comparing ' + filename + '' + str(e))
        Report_file.add_line('Error while comparing ' + filename + '' + str(e))
        assert False

    finally:
        sftp_client.close()
        abcd_connection.close()


def add_nfvo_configuration_evnfm(app=False):
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
        log.info('Start to add NFVO configuration E-VNFM')

        nfvo_details = Initialization_script.get_model_objects(Initialization_script, 'NFVO')
        core_vm_hostname = nfvo_details._Nfvo__CORE_VM_HOSTNAME
        vm_vnfm_director_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        cd_filepath = f'/home/{Ecm_core.get_vm_vnfm_director_username(Ecm_core)}/post_install_ecm_integration'
        if app == 'TEST-HOTEL':
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_director_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
            director_connection = get_testhotel_vmvnfm_host_connection(vm_vnfm_director_ip,
                                                                       vm_vnfm_director_username)
        else:
            director_connection = get_VMVNFM_host_connection()

        dir_name = 'post_install_ecm_integration'

        ServerConnection.put_folder_scp(director_connection, r'com_ericsson_do_auto_integration_files/' + dir_name,
                                        f'/home/{Ecm_core.get_vm_vnfm_director_username(Ecm_core)}/')

        command = 'cd ' + cd_filepath + ' ; chmod 777 post_install_evnfm.sh '
        log.info('CD Command : %s', command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())

        if is_cloudnative:
            command_to_get_tls_crt = f"cd {cd_filepath}; openssl s_client -connect {core_vm_hostname}:443 < /dev/null 2>/dev/null | openssl x509 -outform PEM > tls.crt"
            log.info('Command to get tls certificate: %s', command_to_get_tls_crt)
            stdin, stdout, stderr = director_connection.exec_command(command_to_get_tls_crt)
            command_output = str(stdout.read())
            log.info('Changing script to unix format')
            command_change_to_unix = 'cd ' + cd_filepath + "; sed $'s/\\r$//' post_install_evnfm.sh > post_install_evnfm.unix.sh"
            log.info('command to change to unix format: %s', command_change_to_unix)
            stdin, stdout, stderr = director_connection.exec_command(command_change_to_unix)
            command_output = str(stdout.read())
            log.info('Output of command to change format: %s', command_output)
            command = f"cd {cd_filepath} ; chmod 777 post_install_evnfm.unix.sh"
            stdin, stdout, stderr = director_connection.exec_command(command)
            command_output = str(stdout.read())
            command = f"cd {cd_filepath} ; ./post_install_evnfm.unix.sh {vm_vnfm_namespace} {core_vm_hostname} {vm_vnfm_director_username}"
            log.info('Command to run the script: %s', command)
            stdin, stdout, stderr = director_connection.exec_command(command)
            command_output = str(stdout.read().decode('utf-8'))

        else:
            command = f"cd {cd_filepath} ; ./post_install_evnfm.sh {vm_vnfm_namespace} {core_vm_hostname} {vm_vnfm_director_username}"
            log.info('Command : %s', command)
            stdin, stdout, stderr = director_connection.exec_command(command)
            command_output = str(stdout.read())

        log.info('NFVO post install Command Output : %s', command_output)

        if "created" in command_output:
            log.info('NFVO configuration is successful ...')

        elif "NAME" in command_output and "TYPE" in command_output and "DATA" in command_output:
            log.info('Already installed.')

        else:
            log.error('Something wrong in configuration , please check command output for details %s', command_output)
            assert False

    except Exception as e:
        log.error('Error while configuring Nfvo: %s', str(e))
        assert False


def register_evnfm_cnf_integration():
    try:
        log.info('Start to Register E-VNFM')

        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        vm_vnfm_manager_name = Common_utilities.get_name_with_timestamp(Common_utilities, vm_vnfm_namespace)
        file_name = 'vm_vnfm_register.json'
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        update_register_vm_vnfm(file_name, vm_vnfm_manager_name, "CNS-INST")

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        log.info('Transferring vm_vnfm_register.json file to blade host server ')

        ServerConnection.put_file_sftp(connection,
                                       r'com_ericsson_do_auto_integration_files/vm_vnfm/' + file_name,
                                       f'{SIT.get_base_folder(SIT)}{file_name}')

        time.sleep(2)
        log.info('Generating token to register VM VNFM ')

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @vm_vnfm_register.json https://{}/ecm_service/vnfms'''.format(
            token, core_vm_hostname)

        log.info('Register VM VNFM with curl command : %s', command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('register command output : %s', command_output)

        output = ast.literal_eval(command_output[2:-1:1])

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            subscription_string = ast.literal_eval(command_output[2:-1:1])
            if 'data' in subscription_string.keys():
                vnfm_id = subscription_string['data']['vnfm']['id']
                log.info('vm vnfm id  :' + vnfm_id)

                log.info('updating run time file with VN VNFM id ')
                update_runtime_env_file('CNF_VNFM_ID', vnfm_id)



        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for registering the VM VNFM ' + command_error)
            assert False

    except Exception as e:

        log.error('Error while registering e-vnfm')
        assert False

    finally:
        connection.close()


def restart_pods_eocm():
    director_connection = None
    try:
        log.info('Initiating rollout command for pods restart')
        eocm_namespace = Ecm_core.get_ecm_namespace(Ecm_core)
        deployment_name = 'eric-eo-cm-onboarding'
        rollout_cmd = f'kubectl rollout restart -n {eocm_namespace} deployment/{deployment_name}'
        log.info('Command to restart pods: %s', rollout_cmd)
        director_connection = get_VMVNFM_host_connection()

        stdin, stdout, stderr = director_connection.exec_command(rollout_cmd)
        command_output = str(stdout.read())
        command_output_err = str(stderr.read())
        log.info('command output: %s', command_output)
        log.info('command output: %s', command_output_err)

        if 'eric-eo-cm-onboarding restarted' in command_output:
            log.info('Pods have been restarted successfully')
        else:
            log.error('Pods restart failed due to above error')
            assert False

    except Exception as e:
        log.error('Error while restarting pods in EOCM due to exception: %s', str(e))
        assert False

    finally:
        director_connection.close()
