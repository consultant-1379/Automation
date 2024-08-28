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
Created on 10 feb 2018

@author: eshetra

'''
import random
import time
import ast
import subprocess
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *

log = Logger.get_logger('DC_GATEWAY')


def change_activation_gui_password():
    try:
        log.info('Starting the script to change activation gui password')
        Report_file.add_line('Starting the script to change activation gui password...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        log.info('Generate bearer token to check if default password is changed')
        Report_file.add_line('Generate bearer token to check if default password is changed...')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.model_catalog.write&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Generate bearer token to check if default password is changed...' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        if "error" in output.keys():
            log.info('Bearer Token generation failed.So proceeding to change the default password' + command_output)
            Report_file.add_line(
                'Bearer Token generation failed.So proceeding to change the default password  :' + command_output)
            file_name = r'activation_gui_password.json'
            update_activation_gui_password(file_name)

            sftp = connection.open_sftp()
            sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
            sftp.close()
            log.info('Start changing default activation GUI password')
            Report_file.add_line('Start changing default activation GUI password...')
            curl = '''curl -k --request POST --url https://{}:8383/oauth/login/renew --header 'Cache-Control: no-cache' --header 'Content-Type: application/json' --data @{}'''.format(
                activation_vm_ip, file_name)
            command = curl
            Report_file.add_line('Start changing default activation GUI password using curl:..' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            log.info('Checking if Activation gui password is changed')
            Report_file.add_line('Check...')
            curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.model_catalog.write&undefined={}'''.format(
                activation_vm_ip, act_gui_username, act_gui_password, "'")
            command = curl
            Report_file.add_line('Generate bearer token to check if activation gui password is changed...')
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = command_output[2:-1:1]

            output = ast.literal_eval(command_out)

            if "error" in output.keys():
                log.error('Bearer Token generation failed.So activation gui password change failed :' + command_output)
                Report_file.add_line(
                    'Bearer Token generation failed.So activation gui password change failed :' + command_output)
                assert False
            else:
                token = output['access_token']
                log.info(
                    'Bearer Token generation is successfull.So activation gui password change is successfull :' + command_output)
                Report_file.add_line(
                    'Bearer Token generation is successfull.So activation gui password change is successfull :' + token)
        else:
            log.info(
                'Bearer Token generation is successful. So skipping the default password change for activation GUI')
            Report_file.add_line(
                'Bearer Token generation is successful.So skipping the default password change for activation GUI :')


    except Exception as e:
        log.error('Error executing GUI password change  ' + str(e))
        Report_file.add_line('Error executing GUI password change  ' + str(e))
        assert False

    finally:
        connection.close()


def update_activation_gui_password_eocm():
    """
    This method is used to update the activation gui new password in EOCM 
    It will run twice for HA env and verification based on decripted password
    """
    try:
        log.info('Start updating activation GUI password EOCM')

        deployment_type = Server_details.get_deployment_type(Server_details)

        run = 0
        core_vm_2 = False
        while run <= 1:

            server_ip, username, password = Server_details.core_vm_details(Server_details, core_vm_2)

            connection = ServerConnection.get_connection(server_ip, username, password)

            interact = connection.invoke_shell()

            command = 'su ecm_admin'
            Report_file.add_line(command)
            interact.send(command + '\n')
            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            Report_file.add_line(buff)

            command = '''/app/ecm/tools/.enc-util/update_properties.py -e $JBOSS_HOME/modules/com/ericsson/configuration/main/core_config.properties -o $JBOSS_HOME/modules/com/ericsson/configuration/main/rest-services.properties -p 'Activation!234' -m encrypt -n SCM_ADMIN_PASSWORD'''
            Report_file.add_line(command)
            interact.send(command + '\n')
            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            Report_file.add_line(buff)

            command = '''sudo systemctl restart jboss-eap'''
            Report_file.add_line(command)
            interact.send(command + '\n')
            log.info('waiting 300 seconds for jboss restart')
            time.sleep(300)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            Report_file.add_line(buff)

            command = ''' sudo systemctl restart vim-capacity vim-discovery wf-mgmt'''
            Report_file.add_line(command)
            interact.send(command + '\n')
            log.info('waiting 180 seconds for vim-capacity restart')
            time.sleep(180)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            Report_file.add_line(buff)

            log.info('Going to fetch updated encripted password from server')
            log.info('Checking JBOSS_HOME directory')

            command = "env |grep JBOSS_HOME|awk -F= '{print $2}'"
            Report_file.add_line(command)
            stdin, stdout, stderr = connection.exec_command(command)
            jboss_home = stdout.read().decode("utf-8").strip()
            log.info('JBOSS_HOME directory is %s', jboss_home)

            command = f'''cat {jboss_home}/modules/com/ericsson/configuration/main/rest-services.properties | grep SCM_ADMIN_PASSWORD'''

            log.info(f'command is {command}')

            Report_file.add_line(command)
            stdin, stdout, stderr = connection.exec_command(command)

            command_output = str(stdout.read())

            Report_file.add_line(command_output)

            encripted_password = command_output[2:-3:1].split("SCM_ADMIN_PASSWORD=")[1]

            log.info('Password we got after update : %s', encripted_password)

            command = f'''echo {encripted_password} > /tmp/decript_file.txt'''

            Report_file.add_line(command)

            stdin, stdout, stderr = connection.exec_command(command)

            log.info('Going  to fetch decript password ')
            command = '''/app/ecm/tools/.enc-util/isibalo.py -f /tmp/decript_file.txt -m get'''

            Report_file.add_line(command)

            stdin, stdout, stderr = connection.exec_command(command)

            command_output = str(stdout.read())

            Report_file.add_line(command_output)

            decript_password = command_output[2:-3:1]
            log.info('Password we got after decription : %s', decript_password)

            connection.close()

            if "Activation!234" == decript_password:
                log.info(f'Successfully updated the password on core vm IP : {server_ip}')
                Report_file.add_line(f'Successfully updated the password on core vm IP : {server_ip}')
            else:
                log.error(f'Error updating the password on core vm IP : {server_ip}')
                assert False

            if "HA" == deployment_type:
                run = run + 1
                core_vm_2 = True
                if run != 2:
                    log.info("This is HA env , now going to connect with core vm 2 for performing same task ")
                    Report_file.add_line(
                        "This is HA env , now going to connect with core vm 2 for performing same task ")
            else:
                break

    except Exception as e:
        log.error('Error updating activation GUI password EOCM  %s', str(e))
        Report_file.add_line('Error updating activation GUI password EOCM ' + str(e))
        assert False


def check_feature_model():
    try:

        log.info('Starting to check feature model')
        Report_file.add_line('Starting to check feature model...')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generate Bearer Token to check if feature models are present')
        Report_file.add_line('Generate Bearer Token to Check if feature models are present...')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.model_catalog.read&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Start generating bearer token to check if  feature models are present:..' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        if "error" in output.keys():
            log.error('Bearer Token generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation failed  :' + command_output)
            assert False
        else:
            token = output['access_token']
            log.info('Bearer Token generation is success :' + command_output)
            Report_file.add_line('Bearer Token generation is success  :' + token)

        log.info('Checking if feature models are present using the token' + token)
        Report_file.add_line('Checking if feature models are present using the token' + token)
        curl = '''curl --insecure 'https://{}:8383/scm-rest/modelcatalog/models?pageIndex=1&pageSize=50' -H 'Authorization: Bearer {}' -H 'Accept: application/json{}'''.format(
            activation_vm_ip, token, "'")
        command = curl
        Report_file.add_line('Curl command to check feature model:' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        log.info(command_output)
        feature_list = ['Interface', 'StaticRoute', 'types']

        item_list = output['listItems']
        new_feature_list = []

        for i in range(len(item_list)):
            name1 = item_list[i]['name']
            new_feature_list.append(name1)

        check = all(item in new_feature_list for item in feature_list)

        if check is True:
            log.info('Feature models are present. Skipping creation :' + command_output)
            Report_file.add_line('Feature models are present. Skipping creation:' + command_output)
        else:
            log.error('Feature models doesnot exists. Proceeding to create Feature model :' + command_output)
            Report_file.add_line(
                'Feature model doesnot exists. Proceeding to create feature models  :' + command_output)
            import_feature_model()

    except Exception as e:
        log.error('Error checking feature model  ' + str(e))
        Report_file.add_line('Error checking feature model ' + str(e))
        assert False

    finally:
        connection.close()


def check_device_type():
    try:

        log.info('Starting to check if device type exists')
        Report_file.add_line('Starting to check if device type already exists...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generate Bearer Token to check if  device type exists')
        Report_file.add_line('Generate Bearer Token to check if  bearer token exists...')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.device_type_management.read&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Start generating bearer token to check if device type  exists:..' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        if "error" in output.keys():
            log.error('Bearer Token generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation failed  :' + command_output)
        else:
            token = output['access_token']
            log.info('Bearer Token generation is success :' + command_output)
            Report_file.add_line('Bearer Token generation is success  :' + token)
        log.info('Generate Bearer Token to delete if  device type exists')
        Report_file.add_line('Generate Bearer Token to delete if  bearer token exists...')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.device_type_management.write&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Start generating bearer token to check if device type  exists:..' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        if "error" in output.keys():
            log.error('Bearer Token generation to delte device type failed :' + command_output)
            Report_file.add_line('Bearer Token generation to delete device type failed  :' + command_output)
        else:
            token1 = output['access_token']
            log.info('Bearer Token generation to delete device type is success :' + command_output)
            Report_file.add_line('Bearer Token generation to delete device type is success  :' + token)

        log.info('Checking if device type exists using the token' + token)
        Report_file.add_line('Device type check using the token' + token)
        # curl = '''curl --insecure 'https://{}:8383/scm-rest/modelcatalog/models?pageIndex=1&pageSize=50' -H 'Authorization: Bearer {}' -H 'Accept: application/json{}'''.format(activation_vm_ip,token,"'")
        curl = '''curl --insecure "https://{}:8383/scm-rest/template-management/device-types" -H "Accept: application/json" -H 'Authorization: Bearer {}{}'''.format(
            activation_vm_ip, token, "'")
        command = curl
        Report_file.add_line('Curl command to check if Device type exists:' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)
        Report_file.add_line('Device type check output: ' + command_output)
        log.info(command_output)

        if 'TEMPLATE_ASR' in output:
            log.info('Device type with name TEMPLATE_ASR exists. Proceeding to delete device type' + command_output)
            Report_file.add_line(
                'Device type with name TEMPLATE_ASR exists.Proceeding to delete device type' + command_output)
            curl = '''curl --insecure "https://{}:8383/scm-rest/template-management/device-types/TEMPLATE_ASR" -X DELETE -H "Accept: */*" -H "Content-Type: application/json" -H 'Authorization: Bearer {}{}'''.format(
                activation_vm_ip, token1, "'")
            command = curl
            Report_file.add_line('Curl command to delete device type:' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            time.sleep(5)

        else:
            log.info('Device type with name TEMPLATE_ASR doesnot exists' + command_output)
            Report_file.add_line('Device type with name TEMPLATE_ASR doesnot exists' + command_output)


    except Exception as e:
        log.error('Error checking device type  ' + str(e))
        Report_file.add_line('Error checking device type  ' + str(e))
        assert False

    finally:
        connection.close()


def import_feature_model():
    try:

        log.info('Starting to import feature model')
        Report_file.add_line('Starting to import feature model...')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        dcgw_software_path = sit_data._SIT__dcgw_software_path
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generate bearer token to Start importing Interface, Static routes and type feature models')
        Report_file.add_line(
            'Generate bearer token to Start importing Interface, Static routes and type feature models...')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.model_catalog.write&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line(
            'Generate bearer token to Start importing Interface, Static routes and type feature models...')
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        if "error" in output.keys():
            log.error('Bearer Token generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation failed  :' + command_output)
            assert False
        else:
            token = output['access_token']
            log.info('Bearer Token generation is successfull :' + command_output)
            Report_file.add_line('Bearer Token generation is successfull :' + token)

        log.info('Start importing Interface, Static routes and type feature models')
        Report_file.add_line('Start importing Interface, Static routes and type feature models...')
        curl = '''curl -X POST --insecure https://{}:8383/scm-rest/modelcatalog/models/import/all -H 'Authorization: Bearer {}' -H 'Content-Type: multipart/form-data' -H 'cache-control: no-cache' -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' -F 'file=@{}/models.zip{}'''.format(
            activation_vm_ip, token, dcgw_software_path, "'")
        command = curl
        Report_file.add_line('Start importing Interface, Static routes and type feature models using curl:..' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        print('waiting for 15 secs')
        time.sleep(15)

        log.info('Generate Bearer Token for feature model verification')
        Report_file.add_line('Generate Bearer Token for feature model verification...')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.model_catalog.read&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Start generating bearer token to verify feature model verification:..' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        if "error" in output.keys():
            log.error('Bearer Token generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation failed  :' + command_output)
            assert False
        else:
            token = output['access_token']
            log.info('Bearer Token generation is success :' + command_output)
            Report_file.add_line('Bearer Token generation is success  :' + token)

        log.info('feature model verification using the token' + token)
        Report_file.add_line('feature model verification using the token' + token)
        curl = '''curl --insecure 'https://{}:8383/scm-rest/modelcatalog/models?pageIndex=1&pageSize=50' -H 'Authorization: Bearer {}' -H 'Accept: application/json{}'''.format(
            activation_vm_ip, token, "'")
        command = curl
        Report_file.add_line('Curl command to verify feature model:' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)
        log.info(command_output)
        feature_list = ['Interface', 'StaticRoute', 'types']

        item_list = output['listItems']
        new_feature_list = []

        for i in range(len(item_list)):
            name1 = item_list[i]['name']
            new_feature_list.append(name1)

        check = all(item in new_feature_list for item in feature_list)

        if check is True:
            log.info('Feature model verification is success :' + command_output)
            Report_file.add_line('Feature model verification is success  :' + command_output)
        else:
            log.error('Feature model verification is failed :' + command_output)
            Report_file.add_line('Feature model verification is failed  :' + command_output)
            assert False

    except Exception as e:
        log.error('Error executing import feature model  ' + str(e))
        Report_file.add_line('Error executing import feature model ' + str(e))
        assert False

    finally:
        connection.close()


def check_template():
    try:

        log.info('Starting to check if templates exists')
        Report_file.add_line('Starting to check if templates exists...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        log.info('Generate Bearer Token to check if template exists')
        Report_file.add_line('Generate Bearer Token to check if template exists')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.template_management.read&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Curl command to Generate Bearer Token to check if template exists.' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        log.info(command_output)

        if "error" in output.keys():
            log.error('Bearer Token generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation failed  :' + command_output)
        else:
            token = output['access_token']
            log.info('Bearer Token generation is success :' + command_output)
            Report_file.add_line('Bearer Token generation is success  :' + token)

        Report_file.add_line('Generate Bearer Token to delete if template exists')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.template_management.write&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Curl command to Generate Bearer Token to delete if template exists.' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        log.info(command_output)

        if "error" in output.keys():
            log.error('Bearer Token to delete template generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation to delete template failed  :' + command_output)
            assert False
        else:
            token1 = output['access_token']
            log.info('Bearer Token generation to delete template is success :' + command_output)
            Report_file.add_line('Bearer Token generation to delete template is success  :' + token)
        log.info('Checking if template already exists using the token' + token)
        Report_file.add_line('Checking if template already exists using the token' + token)
        curl = '''curl --insecure "https://{}:8383/scm-rest/template-management/templates?pageIndex=1&pageSize=50" -H  'Authorization: Bearer {}' -H 'Accept: application/json{}'''.format(
            activation_vm_ip, token, "'")
        command = curl
        Report_file.add_line('Curl command to Check if template already exists:' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)

        log.info(command_output)

        item_list = output['listItems']
        if len(item_list) != 0:
            try:
                found = False
                for item in item_list:
                    if 'TEMPLATE_ASR' == item['name']:
                        found = True

                if found:
                    log.info('Template already exists. Deleting Template : TEMPLATE_ASR')
                    Report_file.add_line('Template already exists. Deleting the template : TEMPLATE_ASR')
                    curl = '''curl --insecure 'https://{}:8383/scm-rest/template-management/templates/TEMPLATE_ASR' -X DELETE -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Authorization: Bearer {}{}'''.format(
                        activation_vm_ip, token1, "'")
                    command = curl
                    Report_file.add_line('Curl command to delete template.' + command)
                    command_output = ExecuteCurlCommand.get_json_output(connection,
                                                                        command)
                    time.sleep(5)
                else:
                    log.info('Template doesnot  exists')
                    Report_file.add_line('Template doesnot  exists')

            except:
                log.error('ERROR while checking templates')
        else:
            Report_file.add_line('Template doesnot  exists')

    except Exception as e:
        log.error('Error while checking template  ' + str(e))
        Report_file.add_line('Error while checking template ' + str(e))
        assert False

    finally:
        connection.close()


def upload_template():
    try:

        log.info('Starting to check if templates exists')
        Report_file.add_line('Starting to check if templates exists...')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        dcgw_software_path = sit_data._SIT__dcgw_software_path
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generate Bearer Token for Template upload')
        Report_file.add_line('Generate Bearer Token for Template upload')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.template_management.write&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Generate Bearer Token for Template upload using curl' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        if "error" in output.keys():
            log.error('Bearer Token generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation failed  :' + command_output)
            assert False
        else:
            token = output['access_token']
            log.info('Bearer Token generation is successfull :' + command_output)
            Report_file.add_line('Bearer Token generation is successfull :' + token)

            log.info(
                'To import template with device type : templates.zip file [including device types] using the token')
            Report_file.add_line(
                'To import template with device type : templates.zip file [including device types] using the token...')
            curl = '''curl -X POST --insecure https://{}:8383/scm-rest/template-management/oldimport -H 'Authorization: Bearer {}' -H 'Content-Type: multipart/form-data' -H 'cache-control: no-cache' -H 'content-type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW' -F 'file=@{}/templates.zip{}'''.format(
                activation_vm_ip, token, dcgw_software_path, "'")
            command = curl
            Report_file.add_line('Curl command to import template with device' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            print('waiting for 15 secs')
            time.sleep(15)

            log.info('Generate Bearer Token  for template verification')
            Report_file.add_line('Generate Bearer Token  for template verification')
            curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.template_management.read&undefined={}'''.format(
                activation_vm_ip, act_gui_username, act_gui_password, "'")
            command = curl
            Report_file.add_line('Curl command to generate bearer token to verify template.' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = command_output[2:-1:1]

            output = ast.literal_eval(command_out)

            log.info(command_output)

            if "error" in output.keys():
                log.error('Bearer Token generation failed :' + command_output)
                Report_file.add_line('Bearer Token generation failed  :' + command_output)
            else:
                token = output['access_token']
                log.info('Bearer Token generation is success :' + command_output)
                Report_file.add_line('Bearer Token generation is success  :' + token)

                log.info('Template verification using the token' + token)
                Report_file.add_line('Template verification using the token' + token)
                curl = '''curl --insecure "https://{}:8383/scm-rest/template-management/templates?pageIndex=1&pageSize=50" -H  'Authorization: Bearer {}' -H 'Accept: application/json{}'''.format(
                    activation_vm_ip, token, "'")
                command = curl
                Report_file.add_line('Curl command to verify template:' + command)

                command_output = ExecuteCurlCommand.get_json_output(connection, command)
                command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
                output = ast.literal_eval(command_out)

                log.info(command_output)

                item_list = output['listItems']
                if len(item_list) != 0:
                    found = False
                    for item in item_list:
                        if 'TEMPLATE_ASR' == item['name']:
                            found = True

                    if found:
                        log.info('Template verification is successful for TEMPLATE_ASR')
                        Report_file.add_line('Template verification is successful for TEMPLATE_ASR ')
                    else:
                        log.error('Template verification is failed for TEMPLATE_ASR :')
                        Report_file.add_line('Template verification is failed for TEMPLATE_ASR')
                        assert False

                else:
                    Report_file.add_line('Template doesnot exists')
    except Exception as e:
        log.error('Error executing uploading template  ' + str(e))
        Report_file.add_line('Error executing uploading template ' + str(e))
        assert False

    finally:
        connection.close()


def check_device():
    try:

        log.info('Start checking if device exists')
        Report_file.add_line(' Start checking if device exists...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        act_gui_username = ecm_host_data._Ecm_PI__activation_gui_username
        act_gui_password = ecm_host_data._Ecm_PI__activation_gui_password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        # command = 'cat .ecm_passwords | grep -i EDA'
        # stdin, stdout, stderr = connection.exec_command(command)
        # command_output = stdout.read()
        # string_data = command_output.decode("utf-8")
        # output = string_data.split()
        # user = output[0]
        # password = output[1]
        # log.info('Fetched EDA User: '+user)
        # log.info('Fetched EDA Password: '+password)
        # Report_file.add_line(Report_file, 'Fetched EDA User: '+user)
        # Report_file.add_line(Report_file, 'Fetched EDA Password: '+password)

        # data_file = user +':'+ password

        # command = 'echo ' + data_file + ' > eda.txt'
        # stdin, stdout, stderr = connection.exec_command(command)

        # chunk_data = "$(base64 eda.txt)"
        asr_device_name = ecm_host_data._Ecm_PI__asr_device_name
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        log.info('Generate Bearer Token to check  and delete device')
        Report_file.add_line('Generate Bearer token to check and delete  device')
        curl = '''curl -X POST --insecure https://{}:8383/oauth/v1/token -H 'Content-Type: application/x-www-form-urlencoded' -H 'cache-control: no-cache' -d 'client_id=EDA_M2M_PASSWORD_GRANT_CLIENT_b47b731a-62e0-4f12-9421-033758c2c0f7&client_secret=7544c077-a088-416a-83a6-71e3d26082f8&grant_type=password&username={}&password={}&scope=profile%20openid%20scopes.ericsson.com%2Factivation%2Fresource_configuration.device_inventory.devices.delete&undefined={}'''.format(
            activation_vm_ip, act_gui_username, act_gui_password, "'")
        command = curl
        Report_file.add_line('Curl command to generate bearer token to check and delete device.' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = command_output[2:-1:1]

        output = ast.literal_eval(command_out)

        log.info(command_output)

        if "error" in output.keys():
            log.error('Bearer Token generation failed :' + command_output)
            Report_file.add_line('Bearer Token generation failed  :' + command_output)
        else:
            token = output['access_token']
            log.info('Bearer Token generation is success :' + command_output)
            Report_file.add_line('Bearer Token generation is success  :' + token)
        # connection = Server_connection.get_connection(Server_connection, ecm_server_ip, ecm_username, ecm_password)
        log.info('Checking if device already exists : ' + asr_device_name)
        Report_file.add_line('Checking if device already exists  : ' + asr_device_name)

        curl = '''curl --insecure "https://{}:8383/scm-rest/device-repository/devices?pageSize=50&pageIndex=1" -H "Accept: application/json" -H 'Authorization: Basic ZWNtQWN0OmVtYUVjbSEyMw=={}'''.format(
            activation_vm_ip, "'")

        command = curl
        Report_file.add_line('Checking the device using the curl :' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Output :' + command_output)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        item_list = output['listItems']
        if len(item_list) != 0:
            try:
                for i in range(len(item_list)):
                    device_name = item_list[i]['masterIdentifier']
                    if device_name == asr_device_name:
                        log.info('Device exists. Deleting the device: ')
                        Report_file.add_line('Device exists. Deleting the device:')
                        curl = '''curl --insecure "https://{}:8383/scm-rest/device-repository/devices?devices"%"5B"%"5D={}" -X DELETE -H "Accept: */*" -H "Content-Type: application/json" -H "Authorization: Bearer {}" -H 'Connection: keep-alive{}'''.format(
                            activation_vm_ip, asr_device_name, token, "'")
                        command = curl
                        Report_file.add_line('Deleting the existing device using the curl :' + command)
                        command_output = ExecuteCurlCommand.get_json_output(connection,
                                                                            command)
                        time.sleep(5)

                        curl = '''curl --insecure "https://{}:8383/scm-rest/device-repository/devices?pageSize=50&pageIndex=1" -H "Accept: application/json" -H 'Authorization: Basic ZWNtQWN0OmVtYUVjbSEyMw=={}'''.format(
                            activation_vm_ip, "'")
                        command = curl
                        Report_file.add_line('Checking the device using the curl :' + command)

                        command_output = ExecuteCurlCommand.get_json_output(connection,
                                                                            command)
                        command_out = ExecuteCurlCommand.get_sliced_command_output(
                            command_output)

                        Report_file.add_line('Checking the device output :' + command_output)
                        output = ast.literal_eval(command_out)
                        item_list = output['listItems']
                        try:
                            for i in range(len(item_list)):
                                device_name = item_list[i]['masterIdentifier']
                                if device_name == asr_device_name:
                                    log.info('Device wasnt deleted using the curl command: ')
                                    Report_file.add_line('Device wasnt deleted using the curl command:')
                                    assert False
                                else:
                                    log.info('Device is now deleted.')
                                    Report_file.add_line('Device is now deleted.')
                        except:
                            log.error('Device is now deleted and doesnot exists')
                            Report_file.add_line('Device is now deleted and does not exists.')
                    else:
                        log.info('Device does not exists.  ')
                        Report_file.add_line('Device does not exists.')
            except:
                log.error('Error executing Device check')
                Report_file.add_line('Error executing Device check.')
        else:
            Report_file.add_line('Device doesnot exists.')
    except Exception as e:
        log.error('Error executing curl command to check device  ' + str(e))
        Report_file.add_line('Error executing curl command to check device  ' + str(e))
        assert False
    finally:
        connection.close()


def create_device():
    try:
        log.info('Start creating device')
        Report_file.add_line(' Start creating device...')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        # command = 'cat .ecm_passwords | grep -i EDA'
        # stdin, stdout, stderr = connection.exec_command(command)
        # command_output = stdout.read()
        # string_data = command_output.decode("utf-8")
        # output = string_data.split()
        # user = output[0]
        # password = output[1]
        # log.info('Fetched EDA User: '+user)
        # log.info('Fetched EDA Password: '+password)
        # Report_file.add_line(Report_file, 'Fetched EDA User: '+user)
        # Report_file.add_line(Report_file, 'Fetched EDA Password: '+password)

        # data_file = user +':'+ password

        # command = 'echo ' + data_file + ' > eda.txt'
        # stdin, stdout, stderr = connection.exec_command(command)

        # chunk_data = "$(base64 eda.txt)"
        file_name = r'createdevice.json'
        update_create_device_file(file_name)
        sftp = connection.open_sftp()
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()
        curl = '''curl --insecure -X POST 'https://{}:8383/scm-rest/device-repository/devices' -H 'Authorization: Basic ZWNtQWN0OmVtYUVjbSEyMw==' -H 'Content-Type: application/json' --data @{}'''.format(
            activation_vm_ip, file_name)

        # curl = '''curl --insecure -X POST https://{}:8383/scm-rest/device-repository/devices -H 'Authorization: {}{}' -H 'Content-Type: application/json' --data @{}'''.format(activation_vm_ip,chunk_data,"=",file_name)
        command = curl
        Report_file.add_mesg('Step', 'Executing the curl command to create device', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        time.sleep(2)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        Report_file.add_line('create device output  : ' + command_out)
        output = ast.literal_eval(command_out)
        requestStatus = output['adminState']
        if 'ACTIVE' in requestStatus:
            log.info('Succesfully created device : ' + command_out)
            Report_file.add_line('Succesfully created device  : ' + command_out)
        else:
            log.error('Failed to create device : ' + command_out)
            Report_file.add_line('Failed to create device : ' + command_out)
            assert False
    except Exception as e:
        log.error('Error executing curl command to create device  ' + str(e))
        Report_file.add_line('Error executing curl command to create device  ' + str(e))
        assert False
    finally:
        connection.close()


def create_network_element():
    try:
        log.info('Start creating network element')
        Report_file.add_line(' Start creating network element...')

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip

        deployment_type = ecm_host_data._Ecm_PI__deployment_type
        if deployment_type == 'HA':
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP

        core_vm_usernae = ecm_host_data._Ecm_PI__CORE_VM_USERNAME
        core_vm_password = ecm_host_data._Ecm_PI__CORE_VM_PASSWORD
        dc_gateway_ne_name = ecm_host_data._Ecm_PI__dcgw_ne_name

        connection = ServerConnection.get_connection(core_vm_ip, core_vm_usernae, core_vm_password)
        token = Common_utilities.accesstoken_dcgw(Common_utilities, connection, core_vm_ip)

        log.info('Network element dont exists, proceeding to create NE with name: ' + dc_gateway_ne_name)
        Report_file.add_line('Network element dont exists, proceeding to create NE with name: ' + dc_gateway_ne_name)

        log.info('Updating createne.json file')
        Report_file.add_line(' Updating createne.json file...')

        file_name = r'createne.json'
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['networkElements', 0], 'host', core_vm_ip)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['networkElements', 0], 'name', dc_gateway_ne_name)

        sftp = connection.open_sftp()
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        log.info('Creating Network ELement')
        Report_file.add_line(' Creating Network ELement...')

        curl = '''curl -X POST "https://{}:8383/oam/v1/networkelements/http-ecm" --insecure -H "Content-Type:application/json"   -H "Authorization:bearer {}" -H "client:ECM" --data @{}'''.format(
            activation_vm_ip, token, file_name)

        command = curl
        Report_file.add_mesg('Step', 'Executing the curl command to create network element', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        time.sleep(4)

        log.info('Verifying creation of network element')
        Report_file.add_line(' Verifying creation of network element...')

        curl = '''curl -X GET "https://{}:8383/oam/v1/networkelements/http-ecm/{}" --insecure -H "Content-Type:application/json"   -H "Authorization:bearer {}" -H "client:ECM"'''.format(
            activation_vm_ip, dc_gateway_ne_name, token)
        command = curl
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        if "msg" in output.keys():
            log.error('Network element creation failed: ')
            Report_file.add_line('Network element creation failed:')
            assert False

        else:
            nename = output['name']
            if nename == dc_gateway_ne_name:
                log.info('Network element is created successfully ' + dc_gateway_ne_name)
                Report_file.add_line('Network element is created successfully ' + dc_gateway_ne_name)
            else:
                print("Network element with proceeding name exists: ' +nename")


    except Exception as e:
        log.error('Error executing curl command to create network element  ' + str(e))
        Report_file.add_line('Error executing curl command to create network element  ' + str(e))
        assert False

    finally:
        connection.close()


def check_network_element():
    try:

        log.info('Start checking if  network element creation is success')
        Report_file.add_line(' Start checking if network element creation is success...')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip

        deployment_type = ecm_host_data._Ecm_PI__deployment_type
        if deployment_type == 'HA':
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP

        core_vm_usernae = ecm_host_data._Ecm_PI__CORE_VM_USERNAME
        core_vm_password = ecm_host_data._Ecm_PI__CORE_VM_PASSWORD
        dc_gateway_ne_name = ecm_host_data._Ecm_PI__dcgw_ne_name

        connection = ServerConnection.get_connection(core_vm_ip, core_vm_usernae, core_vm_password)
        token = Common_utilities.accesstoken_dcgw(Common_utilities, connection, core_vm_ip)

        log.info('Checking if network element creation is successfull')
        Report_file.add_line('Checking if network element creation is successfull...')

        curl = '''curl -X GET "https://{}:8383/oam/v1/networkelements/http-ecm/{}" --insecure -H "Content-Type:application/json"   -H 'Authorization:bearer {}' -H 'client:ECM{}'''.format(
            activation_vm_ip, dc_gateway_ne_name, token, "'")
        command = curl
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        if "msg" in output.keys():
            log.info('Network element creation has failed: ' + dc_gateway_ne_name)
            Report_file.add_line('Network element creation has failed with NE name: ' + dc_gateway_ne_name)
            assert False
        else:
            nename = output['name']
            if nename == dc_gateway_ne_name:
                log.info('Network element creation is successful with NE name: ' + dc_gateway_ne_name)
                Report_file.add_line('Network element creation is successful with NE name: ' + dc_gateway_ne_name)
            else:
                log.info('Network element with proceeding name exists:  ' + nename)
                Report_file.add_line('Network element with proceeding name exists: ' + dc_gateway_ne_name)
                assert False

    except Exception as e:
        log.error('Error executing verification of  network elements')
        Report_file.add_line('Error executing verification of  network elements')
        assert False
    finally:
        connection.close()


def check_route():
    try:
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip

        deployment_type = ecm_host_data._Ecm_PI__deployment_type
        if deployment_type == 'HA':
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP

        core_vm_usernae = ecm_host_data._Ecm_PI__CORE_VM_USERNAME
        core_vm_password = ecm_host_data._Ecm_PI__CORE_VM_PASSWORD
        dc_gateway_ne_name = ecm_host_data._Ecm_PI__dcgw_ne_name

        connection = ServerConnection.get_connection(core_vm_ip, core_vm_usernae, core_vm_password)
        token = Common_utilities.accesstoken_dcgw(Common_utilities, connection, core_vm_ip)
        log.info('Checking if routing creation is successfull')
        Report_file.add_line(' Checking if routing creation is successfull...')
        curl = '''curl -X GET "https://{}:8383/oam/v1/routings/regular-expression/ECM_DCGW" --insecure -H "Content-Type:application/json"   -H "Authorization:bearer {}" -H "client:ECM"'''.format(
            activation_vm_ip, token)
        command = curl
        Report_file.add_mesg('Step', 'Start Verification of routing', command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        if "routingType" in output.keys():
            log.info('Routing verification passed')
            Report_file.add_line('Routing verification passed:')
        else:
            log.error('Routing verification failed')
            Report_file.add_line('Routing  verification failed:')
            assert False

    except Exception as e:
        log.error('Error executing verification of  routing')
        Report_file.add_line('Error executing verification of  route')
        assert False
    finally:
        connection.close()


def deletedbentry():
    try:

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        rdb_vm_ip = ecm_host_data._Ecm_PI__RDB_VM_IP
        rdb_vm_username = ecm_host_data._Ecm_PI__RDB_VM_USERNAME
        rdb_vm_password = ecm_host_data._Ecm_PI__RDB_VM_PASSWORD

        password = Common_utilities.fetch_cmdb_password(Common_utilities)
        os_command = f'ssh-keygen -R {rdb_vm_ip}'
        result = subprocess.run(os_command, shell=True)
        log.info(os_command)
        if result.returncode == 0:
            log.info('Host key successfully removed.')
        else:
            log.info('Error encountered in  os command')
            log.info(result.stderr)
        connection = ServerConnection.get_connection(rdb_vm_ip, rdb_vm_username, rdb_vm_password)
        interact = connection.invoke_shell()
        command = 'psql -d ecmdb1 -U cmdb'
        log.info(command)

        interact.send(command + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'Password for user cmdb' in buff:
            interact.send(password + '\n')
            time.sleep(2)

        command = 'delete from cm_subtype_template_assoc where asset_subtype_id={}DCGW-ASR9000-AST1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_subtype_template_assoc table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_subtype_template_assoc table: ' + command)

        command = 'delete from cm_asset_subtype where id={}DCGW-ASR9000-AST1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_asset_subtype table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_asset_subtype table: ' + command)

        command = 'delete from cm_managed_asset where id={}DCGW-ASR9000-MA1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_managed_asset table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_managed_asset table: ' + command)

        command = 'delete from cm_custom_template where id={}DCGW-ASR9000-CT1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_custom_template table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_custom_template table: ' + command)

        command = 'delete from cm_activation_entity where id={}ASR9000{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_activation_entity table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_activation_entity table: ' + command)

        command = 'delete from cm_activation_manager where id={}DCGW-ASR9000-AM1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_asset_subtype table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_activation_manager table: ' + command)

        command = 'delete from cm_large_object where id={}DCGW-ASR9000-AM1-Attachment{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_large_object table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_large_object table: ' + command)

        command = 'delete from cm_large_object where id={}AE1CPId{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp1 = interact.recv(9999)
        log.info('Starting to delete the entry from cm_large_object table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_large_object table: ' + command)

        interact.shutdown(2)

    except Exception as e:
        log.error('Error while deleting activation entities  ' + str(e))
        Report_file.add_line('Error while deleting activation entities  ' + str(e))
        assert False
    finally:
        connection.close()


def check_dcgw_configuration():
    try:
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        rdb_vm_ip = ecm_host_data._Ecm_PI__RDB_VM_IP
        rdb_vm_username = ecm_host_data._Ecm_PI__RDB_VM_USERNAME
        rdb_vm_password = ecm_host_data._Ecm_PI__RDB_VM_PASSWORD
        password = Common_utilities.fetch_cmdb_password(Common_utilities)
        connection = ServerConnection.get_connection(rdb_vm_ip, rdb_vm_username, rdb_vm_password)
        interact = connection.invoke_shell()
        command = 'psql -d ecmdb1 -U cmdb'
        log.info(command)

        interact.send(command + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'Password for user cmdb' in buff:
            interact.send(password + '\n')
            time.sleep(2)

        command = 'select * from cm_subtype_template_assoc where asset_subtype_id={}DCGW-ASR9000-AST1{};'.format("'",
                                                                                                                 "'")
        interact.send(command + '\n')
        time.sleep(3)
        resp1 = interact.recv(9999)
        buff1 = str(resp1)
        log.info('Starting to check the entry from cm_subtype_template_assoc table:' + command)
        Report_file.add_line('Starting to check the entry from cm_subtype_template_assoc table: ' + command)

        if '1 row' in buff1:
            log.info('Entry is populated on cm_subtype_template_assoc table:' + buff1)
            Report_file.add_line('Entry is populated on cm_subtype_template_assoc table:' + buff1)
        else:
            log.info('Entry is not populated on cm_subtype_template_assoc table:' + buff1)
            Report_file.add_line('Entry is not populated on cm_subtype_template_assoc table:' + buff1)
            assert False

        command = 'select * from cm_asset_subtype where id={}DCGW-ASR9000-AST1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp2 = interact.recv(9999)
        buff2 = str(resp2)
        log.info('Starting to check the entry from cm_asset_subtype table:' + command)
        Report_file.add_line('Starting to check the entry from cm_asset_subtype table: ' + command)

        if '1 row' in buff2:
            log.info('Entry is populated on cm_asset_subtype table:' + buff1)
            Report_file.add_line('Entry is populated on cm_asset_subtype table:' + buff1)
        else:
            log.info('Entry is not populated on cm_asset_subtype table:' + buff1)
            Report_file.add_line('Entry is not populated on cm_asset_subtype table:' + buff1)
            assert False

        command = 'select * from cm_managed_asset where id={}DCGW-ASR9000-MA1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp3 = interact.recv(9999)
        buff3 = str(resp3)
        log.info('Starting to check  the entry from cm_managed_asset table:' + command)
        Report_file.add_line('Starting to check the entry from cm_managed_asset table: ' + command)

        if '1 row' in buff3:
            log.info('Entry is populated on cm_managed_asset table:' + buff3)
            Report_file.add_line('Entry is populated on cm_managed_asset table:' + buff3)
        else:
            log.info('Entry is not populated on cm_managed_asset table:' + buff3)
            Report_file.add_line('Entry is not populated on cm_managed_asset table:' + buff3)
            assert False

        command = 'select * from cm_custom_template where id={}DCGW-ASR9000-CT1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp4 = interact.recv(9999)
        buff4 = str(resp4)
        log.info('Starting to check the entry from cm_custom_template table:' + command)
        Report_file.add_line('Starting to check the entry from cm_custom_template table: ' + command)

        if '1 row' in buff4:
            log.info('Entry is populated on cm_custom_template table:' + buff4)
            Report_file.add_line('Entry is populated on cm_custom_template table:' + buff4)
        else:
            log.info('Entry is not populated on cm_custom_template table:' + buff4)
            Report_file.add_line('Entry is not populated on cm_custom_template table:' + buff4)
            assert False

        command = 'select * from cm_activation_manager where id={}DCGW-ASR9000-AM1{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp5 = interact.recv(9999)
        buff5 = str(resp5)
        log.info('Starting to check the entry from cm_activation_manager table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_activation_manager table: ' + command)
        if '1 row' in buff5:
            log.info('Entry is populated on cm_custom_template table:' + buff5)
            Report_file.add_line('Entry is populated on cm_custom_template table:' + buff5)
        else:
            log.info('Entry is not populated on cm_custom_template table:' + buff5)
            Report_file.add_line('Entry is not populated on cm_custom_template table:' + buff5)
            assert False

        interact.shutdown(2)

    except Exception as e:
        log.error('Error while checking dcgw configuration  ' + str(e))
        Report_file.add_line('Error while checking dcgw configuration  ' + str(e))
        assert False
    finally:
        connection.close()


def check_activation_entities():
    try:

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        rdb_vm_ip = ecm_host_data._Ecm_PI__RDB_VM_IP
        rdb_vm_username = ecm_host_data._Ecm_PI__RDB_VM_USERNAME
        rdb_vm_password = ecm_host_data._Ecm_PI__RDB_VM_PASSWORD

        password = Common_utilities.fetch_cmdb_password(Common_utilities)
        os_command = f'ssh-keygen -R {rdb_vm_ip}'
        log.info(os_command)
        result = subprocess.run(os_command, shell=True)
        if result.returncode == 0:
            log.info('Host key successfully removed.')
        else:
            log.info('Error encountered in  os command')
            log.info(result.stderr)
        connection = ServerConnection.get_connection(rdb_vm_ip, rdb_vm_username, rdb_vm_password)
        interact = connection.invoke_shell()
        command = 'psql -d ecmdb1 -U cmdb'
        log.info(command)

        interact.send(command + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'Password for user cmdb' in buff:
            interact.send(password + '\n')
            time.sleep(2)

        command = 'select * from cm_large_object where id={}DCGW-ASR9000-AM1-Attachment{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp6 = interact.recv(9999)
        buff6 = str(resp6)
        log.info('Starting to check the entry from cm_large_object table:' + command)
        Report_file.add_line('Starting to check the entry from cm_large_object table: ' + command)
        if '1 row' in buff6:
            log.info('Entry is populated on cm_large_object table with id DCGW-ASR9000-AM1-Attachment' + buff6)
            Report_file.add_line(
                'Entry is populated on cm_custom_template table with id DCGW-ASR9000-AM1-Attachment:' + buff6)
        else:
            log.info('Entry is not populated on cm_custom_template table:' + buff6)
            Report_file.add_line('Entry is not populated on cm_custom_template table:' + buff6)
            assert False

        command = 'select * from cm_large_object where id={}AE1CPId{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp7 = interact.recv(9999)
        buff7 = str(resp7)
        log.info('Starting to checking  the entry from cm_large_object table where id is AE1CPId :' + command)
        Report_file.add_line(
            'Starting to checking  the entry from cm_large_object table where id is AE1CPId: ' + command)
        if '1 row' in buff7:
            log.info('Entry is populated on cm_large_object table with id AE1CPId' + buff7)
            Report_file.add_line('Entry is populated on cm_custom_template table with id AE1CPId:' + buff7)
        else:
            log.info('Entry is not populated on cm_large_object table with id AE1CPId:' + buff7)
            Report_file.add_line('Entry is not populated on cm_large_object table with id AE1CPId:' + buff7)
            assert False

        command = 'select * from cm_activation_entity where id={}ASR9000{};'.format("'", "'")
        interact.send(command + '\n')
        time.sleep(6)
        resp8 = interact.recv(9999)
        buff8 = str(resp8)
        log.info('Starting to check the entry from cm_activation_entity table:' + command)
        Report_file.add_line('Starting to delete the entry from cm_activation_entity table: ' + command)
        if '1 row' in buff8:
            log.info('Entry is populated on cm_activation_entity table:' + buff8)
            Report_file.add_line('Entry is populated on cm_activation_entity table:' + buff8)
        else:
            log.info('Entry is not populated on cm_activation_entity table:' + buff8)
            Report_file.add_line('Entry is not populated on cm_activation_entity table:' + buff8)
            assert False

        interact.shutdown(2)

    except Exception as e:
        log.error('Error while checking activation entities  ' + str(e))
        Report_file.add_line('Error while checking activation entities  ' + str(e))
        assert False
    finally:
        connection.close()


def delete_ne_and_route():
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        dcgw_software_path = sit_data._SIT__dcgw_software_path
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip

        deployment_type = ecm_host_data._Ecm_PI__deployment_type
        if deployment_type == 'HA':
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP

        core_vm_username = ecm_host_data._Ecm_PI__CORE_VM_USERNAME
        core_vm_password = ecm_host_data._Ecm_PI__CORE_VM_PASSWORD

        ShellHandler.__init__(ShellHandler, core_vm_ip, core_vm_username, core_vm_password)
        command = 'cd /app/ecm/tools/envs/dcgw/'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = './manage_dcgw_network.py -o delete'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        output1 = str(stderr)

        if 'Failed to delete' in output1:
            log.info('Network and Route deletion failed or doesnot exist' + str(stderr))
            Report_file.add_line('Network and Route deletion failed or doesnot exists ' + str(stderr))
            ShellHandler.__del__(ShellHandler)
        else:
            log.info('Network deletion and Route deletion is successful ')
            Report_file.add_line('Network and Route deletion  is successful')
            ShellHandler.__del__(ShellHandler)

    except Exception as e:
        log.error('Error while deleting Network elements and Routing  ' + str(e))
        Report_file.add_line('Error while deleting Network elements and Routing ' + str(e))
        assert False


def add_ne_and_route():
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        dcgw_software_path = sit_data._SIT__dcgw_software_path
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip

        deployment_type = ecm_host_data._Ecm_PI__deployment_type
        if deployment_type == 'HA':
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP

        core_vm_username = ecm_host_data._Ecm_PI__CORE_VM_USERNAME
        core_vm_password = ecm_host_data._Ecm_PI__CORE_VM_PASSWORD

        ShellHandler.__init__(ShellHandler, core_vm_ip, core_vm_username, core_vm_password)
        command = 'cd /app/ecm/tools/envs/dcgw/'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = './manage_dcgw_network.py'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        log.info('Starting Network and Route creation using command:' + command)
        Report_file.add_line('Starting Network and Route creation using command: ' + command)
        output1 = str(stderr)

        if 'Failed to create' in output1:
            log.info('Network and Route creation Failed' + str(stderr))
            Report_file.add_line('Network and Route creation Failed' + str(stderr))
            ShellHandler.__del__(ShellHandler)
            assert False

        else:
            log.info('Network creation and Route Creation is successful ')
            Report_file.add_line('Network and Route creation is successful')
            ShellHandler.__del__(ShellHandler)
            check_network_element()
            check_route()

    except Exception as e:
        log.error('Error while adding Network elements and Routing  ' + str(e))
        Report_file.add_line('Error while adding Network elements and Routing ' + str(e))
        assert False


def add_activation_managers_entities():
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        dcgw_software_path = sit_data._SIT__dcgw_software_path
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip

        deployment_type = ecm_host_data._Ecm_PI__deployment_type
        if deployment_type == 'HA':
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_HA_IP

        core_vm_username = ecm_host_data._Ecm_PI__CORE_VM_USERNAME
        core_vm_password = ecm_host_data._Ecm_PI__CORE_VM_PASSWORD
        source_filepath = dcgw_software_path + "/dcgw_New.zip"
        destination_filepath = '/app/ecm/tools/envs/dcgw/dcgw_New.zip'

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Copying the dcgw artifacts from host blade to gateway server:' + activation_vm_ip)
        Report_file.add_line('Copying the dcgw artifacts from host blade to gateway server:' + activation_vm_ip)

        filepath = '/' + ecm_username + '/'
        ServerConnection.transfer_folder_between_remote_servers(connection, core_vm_ip, core_vm_username,
                                                                core_vm_password, source_filepath, destination_filepath,
                                                                filepath, "put")

        log.info('Transfered  dcgw_New.zip into core vm server')
        Report_file.add_line('Transfered dcgw_New.zip into core vm server ')
        os_command = f'ssh-keygen -R {core_vm_ip}'
        result = subprocess.run(os_command, shell=True)
        log.info(os_command)
        if result.returncode == 0:
            log.info('Host key successfully removed.')
        else:
            log.info('Error encountered in  os command')
            log.info(result.stderr)
        connection = ServerConnection.get_connection(core_vm_ip, core_vm_username, core_vm_password)
        log.info('Connected with the core vm server' + core_vm_ip)
        interact = connection.invoke_shell()
        resp = interact.recv(9999)
        buff = str(resp)
        command = 'cd /app/ecm/tools/envs/dcgw/'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        command = 'unzip dcgw_New.zip'
        interact.send(command + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        command = 'chown -R ecm_admin:ecm_admin /app/ecm/tools/envs/dcgw'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)

        # log.info('Transferring cmdb-act-manager.yaml:')
        # Report_file.add_line(Report_file,'Transferring cmdb-act-manager.yaml: ')
        # file_name = r'cmdb-act-manager.yaml'

        # sftp = connection.open_sftp()
        # sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, '/app/ecm/tools/envs/dcgw/' + file_name)
        # sftp.close()

        # log.info('Transferring cmdb-act-entities.yaml:')
        # Report_file.add_line(Report_file,'Updating cmdb-act-entities.yamll: ')
        # EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')        cloud_type = EPIS_data._EPIS__cloudManagerType

        # if cloud_type == 'CEE':
        #    file_name = 'cmdb-act-entities.yaml'
        # else:
        #    file_name = 'cmdb-act-entities-RHOS.yaml'

        # sftp = connection.open_sftp()
        # sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, '/app/ecm/tools/envs/dcgw/cmdb-act-entities.yaml')
        # sftp.close()

        interact.shutdown(2)

        log.info('Adding dcgw configuration started : ')
        Report_file.add_line('Adding dcgw configuration started: ')

        ShellHandler.__init__(ShellHandler, core_vm_ip, core_vm_username, core_vm_password)
        command = 'cd /app/ecm/tools/envs/dcgw'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'chmod +x *.py'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'su - ecm_admin'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'cd /app/ecm/tools/envs/dcgw'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = './add_dcgw_configurations.py'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        output = str(stdout)
        output1 = str(stderr)
        if 'Exit Code: 0' in output:
            log.info('Adding dcgw configuration is success : ' + str(stdout))
            Report_file.add_line('Adding dcgw configuration is success : ' + str(stdout))
            ShellHandler.__del__(ShellHandler)
            check_dcgw_configuration()
        else:
            log.error('Adding dcgw configuration is Failed : ' + str(stdout))
            Report_file.add_line('Adding dcgw configuration is Failed: ' + str(stdout))
            Report_file.add_line('Adding dcgw configuration is Failed: ' + str(stderr))
            ShellHandler.__del__(ShellHandler)
            assert False
        log.info('Adding activation entities Started : ')
        Report_file.add_line('Adding activation entities Started: ')
        ShellHandler.__init__(ShellHandler, core_vm_ip, core_vm_username, core_vm_password)
        command = 'su - ecm_admin'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = 'cd /app/ecm/tools/envs/dcgw'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = 'chmod +x *.py'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        command = './add_activation_entities.py'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        output = str(stdout)
        output1 = str(stderr)

        if 'Exit Code: 0' in output:
            log.info('Adding activation entities is successful : ' + str(stdout))
            Report_file.add_line('Adding activation entities is successful: ' + str(stdout))
            ShellHandler.__del__(ShellHandler)
            check_activation_entities()
        else:
            log.error('Adding activation entities failed : ')
            Report_file.add_line('Adding activation entities failed: ' + str(stderr))
            ShellHandler.__del__(ShellHandler)
            assert False
    except Exception as e:
        log.error('Error while adding activation entities  ' + str(e))
        Report_file.add_line('Error while adding activation entities  ' + str(e))
        assert False
    finally:
        connection.close()


def main():
    log.info('Starting script : DC_GATEWAY')
    log.info('Going to fetch user inputs')
    Report_file.add_line('Starting script : DC_GATEWAY')
    log.info('END script : DC_GATEWAY')
    Report_file.add_line('END script : DC_GATEWAY')
