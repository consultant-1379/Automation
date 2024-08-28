'''
Created on 16 Mar 2020

@author: eshetra

'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
import ast
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import random
import time
from com_ericsson_do_auto_integration_utilities.Common_utilities import *
import paramiko
import sys
import subprocess

log = Logger.get_logger('ENM_POST_INSTALLATION')




def add_roles_admin_user():

    log.info('Add roles to admin user ')
    Report_file.add_line('Add roles to admin user')

    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')


    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    environment = ecm_host_data._Ecm_core__enviornment


    enm_hostname = enm_data._Vnfm__authIpAddress
    enm_username = enm_data._Vnfm__authUserName
    enm_password = enm_data._Vnfm__authPassword
    core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP


    log.info('ECM connection open')
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    enm_token = Common_utilities.generate_enm_token(Common_utilities,connection,enm_hostname,enm_username, enm_password)
    log.info('Start adding Roles using ENM token:' + enm_token)
    Report_file.add_line('Start adding roles using ENM token:' + enm_token)


    file_name = r'addRoles.json'
    sftp = connection.open_sftp()
    sftp.put(r'com_ericsson_do_auto_integration_files/'+file_name, SIT.get_base_folder(SIT)+file_name)
    sftp.close()

    curl = '''curl --insecure "https://{}/oss/idm/usermanagement/users/administrator" -X PUT -H "Accept: */*" -H "Content-Type: application/json" -H "Cookie: ssocookie=ssocookie-1; amlbcookie=01; iPlanetDirectoryPro={}" --data @{}'''.format(enm_hostname,enm_token,file_name)
    command = curl
    log.info(command)
    #stdin, stdout, stderr = connection.exec_command(command)
    #Report_file.add_line(Report_file, 'command output : ' + str(stdout.read()))

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)
    log.info(command_output)
    feature_list = ['Amos_Administrator', 'Amos_Operator', 'Scripting_Decoding_Operator', 'Scripting_Operator', 'SECURITY_ADMIN']

    item_list = output['privileges']
    new_feature_list = []

    for i in range(len(item_list)):
        name1 = item_list[i]['role']
        new_feature_list.append(name1)

    check =  all(item in new_feature_list for item in feature_list)

    if check is True:
        log.info('All the Required roles are added to admin user :' + command_output)
        Report_file.add_line('All the Required roles are added to admin user:' + command_output)
    else:
        log.error('Required roles are missing from admin user:' + command_output)
        Report_file.add_line('Required roles are missing from admin user  :' + command_output)
        assert False




def add_license():

    try:

        #sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        enm_post_software_path = sit_data._SIT__enm_software_path
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
        enm_gui_user_name = enm_data._Vnfm__authUserName
        enm_gui_password = enm_data._Vnfm__authPassword
        enm_gui_hostname = enm_data._Vnfm__authIpAddress
        #scripting_vm_ip = sit_data._SIT__oss_master_host_ip
        scripting_vm_ip = sit_data._SIT__ossMasterHostIP
        scripting_vm_username = enm_data._Vnfm__authUserName
        scripting_vm_password = enm_data._Vnfm__authPassword

        log.info('Start to update listLicenseDetailsENM.py file with ENM details ')
        Report_file.add_line('Start to update tart to update listLicenseDetailsENM.py file with ENM details')

        list_file = 'listLicenseDetailsENM.py'
        add_file = 'addLicenseENM.py'
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        replace_string = "session = enmscripting.open('{}').with_credentials(enmscripting.UsernameAndPassword('{}','{}'))".format(enm_gui_hostname,enm_gui_user_name,enm_gui_password)
        command = 'sed -i -e "/enmscripting.open/c\{}" {}{}'.format(replace_string,enm_post_software_path,list_file)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        connection.exec_command(command)


        log.info('Start to update addLicenseENM.py file with ENM details ')
        Report_file.add_line('Start to update tart to update addLicenseENM.py file with ENM details')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        replace_string = "session = enmscripting.open('{}').with_credentials(enmscripting.UsernameAndPassword('{}','{}'))".format(enm_gui_hostname,enm_gui_user_name,enm_gui_password)
        command = 'sed -i -e "/enmscripting.open/c\{}" {}{}'.format(replace_string,enm_post_software_path,add_file)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        connection.exec_command(command)

        # command to clear the ip from ssh_host file
        remove_ip = 'ssh-keygen -R {}'.format(scripting_vm_ip)
        connection.exec_command(remove_ip)


        #source_filepath = enm_post_software_path + "/" + 'listLicenseDetailsENM.py '+enm_post_software_path+' + "/" + addLicenseENM.py  '+enm_post_software_path+' + "/" + multi_license.txt'
        source_filepath = enm_post_software_path + "/" + 'listLicenseDetailsENM.py '+enm_post_software_path+'/addLicenseENM.py  '+enm_post_software_path+'/multi_license.txt'
        destination_filepath = '/var/tmp/'
        
       
        log.info('Copying the python files required for license install to scripting server:' + scripting_vm_ip)
        Report_file.add_line('Copying the python files required for license install to scripting server:' + scripting_vm_ip)


        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        
        filepath = '/'+ecm_username+'/'
        ServerConnection.transfer_folder_between_remote_servers(connection, scripting_vm_ip, scripting_vm_username, scripting_vm_password, source_filepath, destination_filepath, filepath, "put")
        
        nested_conn = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username, ecm_password, scripting_vm_ip, scripting_vm_username, scripting_vm_password)

        time.sleep(2)

        stdin, stdout, stderr = nested_conn.exec_command("cd /var/tmp; python listLicenseDetailsENM.py")
        command_output = str(stdout.read())
        print(command_output)


        if 'No license found.' in command_output:
            log.info('License is not installed.Proceeding to install the license:' + command_output)
            Report_file.add_line('License is not installed.Proceeding to install the license:' + command_output)

            nested_conn = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username, ecm_password, scripting_vm_ip, scripting_vm_username, scripting_vm_password)

            stdin, stdout, stderr = nested_conn.exec_command("cd /var/tmp; python addLicenseENM.py")
            time.sleep(15)

            command_output = str(stdout.read())
            print(command_output)


            output2 = str(stderr.read())
            print(output2)

            if 'license(s) successfully installed' in command_output:

                log.info('ENM License is successfully installed' + command_output)
                Report_file.add_line('ENM License is successfully installed.' + command_output)
                nested_conn.close()

            else:
                log.info('ENM License installation failed :' + output2)
                Report_file.add_line('ENM License installation failed :' + command_output)
                nested_conn.close()

        else:
            log.info('ENM License is already installed.Skipping the license install step ' + command_output )
            Report_file.add_line('ENM License is already installed.Skipping the license install step ' + command_output)
            nested_conn.close()




    except Exception as e:
        log.error('Error while adding license to ENM server  '+str(e))
        Report_file.add_line('Error while adding license to ENM server ' + str(e))
        assert False



def add_pem_key_file():

    try:
        log.info('start creating private_key.pem file on enm vnflaf services vm server ')
        Report_file.add_line('start creating private_key.pem file on enm vnflaf services vm server')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        lcm_service_data = Initialization_script.get_model_objects(Initialization_script, 'LCM_SERVICE')
        server_ip = lcm_service_data._LCM_service__lcm_service_ip
        username = lcm_service_data._LCM_service__lcm_user_name
        password = lcm_service_data._LCM_service__lcm_password
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        enm_software_path = sit_data._SIT__enm_software_path

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        deployment_name = ecm_host_data._Ecm_PI__vm_deployment_name


        
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
       
        log.info('Copying keyscript.sh into enm vnflaf services vm server ')
        Report_file.add_line('Copying keyscript.sh into enm vnflaf services vm server: ')

        source_filepath = enm_software_path + "/" + "keyscript.sh"
        destination_filepath = '/var/tmp/'
        
        ServerConnection.transfer_files_with_user_and_passwd(connection, username, password, source_filepath, server_ip, destination_filepath)
       
       
        connection.close()


        connection = ServerConnection.get_connection(server_ip, username, password)
        fileExists = ServerConnection.file_exists(server_ip, username, password,
                                               '/var/tmp/private_key.pem')
        if fileExists:

            #log.info('Creating backup of private_key.pem file at path /var/tmp/ ')
            log.info('private_key.pem file already exists.Skipping creation')
            Report_file.add_line('private_key.pem already exists on /var/tmp/')


            #command = 'sudo -i mv /var/tmp/private_key.pem /var/tmp/private_key.pem.orig1'
            #connection.exec_command(command, get_pty=True)
            #Report_file.add_mesg(Report_file, 'Step 1 ', 'Created backup of private_key.pem to private_key.pem.orig ',
            #                 command)
            #log.info('Created backup of private_key.pem to private_key.pem.orig ')
        else:
            log.info('private_key.pem file doesnot exists.Proceeding to create')
            Report_file.add_line('private_key.pem doesnot exist in /var/tmp/. Proceeding to create')

            command = 'sudo -i chmod +x /var/tmp/keyscript.sh'
            connection.exec_command(command, get_pty=True)
            log.info('Given full permission on keyscript.sh :' + command)

            command = '/var/tmp/keyscript.sh {}'.format(deployment_name)
            connection.exec_command(command, get_pty=True)
            time.sleep(8)
            log.info('Executed keyscript.sh :' + command)


        #connection = Server_connection.get_connection(Server_connection, server_ip, username, password)
            fileExists = ServerConnection.file_exists(server_ip, username, password,
                                               '/var/tmp/private_key.pem')
            if fileExists:
                log.info('private_key.pem file successfully created on /var/tmp/ ')
                Report_file.add_line('private_key.pem successfully created on /var/tmp/')

            else:
                log.info('private_key.pem file is not created on /var/tmp')
                Report_file.add_line('private_key.pem file is not created on /var/tmp directory')
                assert False

    except Exception as e:
        connection.close()
        log.error('Error to check and create private_key.pem file')
        Report_file.add_line('Error to check and create private_key.pem')
        assert False

