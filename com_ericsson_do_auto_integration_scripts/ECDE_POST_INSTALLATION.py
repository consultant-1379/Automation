'''
Created on Sep 04, 2020

@author: emaidns
'''


from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import *
from com_ericsson_do_auto_integration_utilities.ECDE_files_update import *




log = Logger.get_logger('ECDE_POST_INSTALLATION.py')




def update_admin_password_first_login():
    change_ecde_password_first_login('admin')


def update_vendor_server_heap():
    update_standalone_conf_ecde()


def create_ecde_node_vendor():
    try:
        log.info('Start creating the vendor')
        Report_file.add_line('Start creating the vendor')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_vendor.json'
        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/vendors' -d @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '201 Created' in command_output:
            log.info(f'vendor has been created sucessfully')
            Report_file.add_line(f'vendor has been created sucessfully ')
        elif 'error.recordWithSameName' in command_output:
            log.info(f'vendor is already created ')
            Report_file.add_line(f'vendor is already created ')
        else:
            log.error('Error creating vendor with output  ' + command_output)
            Report_file.add_line('Error in curl uploading the vendor_product resources ' + command_output)
            assert False

        global vendor_id

        vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

    except Exception as e:
        log.error('Error creating vendor with exception mesg '+str(e))
        Report_file.add_line('Error creating vendor with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()




def create_ecde_node_vendor_user():
    try:
        log.info('Start creating the vendor user')
        Report_file.add_line('Start creating the vendor user')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_vendor_user.json'

        update_vendor_user_file(file_name,vendor_id)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/avop-users' -d @{file_name}'''


        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '201 Created' in command_output:
            log.info('Finished creating the vendor user')
            Report_file.add_line('Finished creating the vendor user')
        elif 'error.userexists' in command_output:
            log.info('User with name AUTO_USER is already exists')
            Report_file.add_line('User with name AUTO_USER is already exists')
        else:
            log.error('Error in curl creating the vendor user  ' + command_output)
            Report_file.add_line('Error in curl creating the vendor user ' + command_output)
            assert False


    except Exception as e:
        log.error('Error creating vendor user with exception mesg '+str(e))
        Report_file.add_line('Error creating vendor user with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()



def update_vendor_password_first_login():
    change_ecde_password_first_login('vendor')

