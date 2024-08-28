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

# This file is for other team for specific task only.

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SO_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *

log = Logger.get_logger('SO_RANDOM_OPERATIONS.py')


def onboard_so_subsytems():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnf_type = sit_data._SIT__vnf_type

    if vnf_type == 'SOL005_EOCM':
        log.info('Going to on-board sol005 subsystem %s', vnf_type)
        Report_file.add_line('Going to on-board subsystem - ' + vnf_type)
        onboard_enm_ecm_subsystems('SOL005_subsystem')
    else:
        log.info('Going to on-board subsystem %s', vnf_type)
        Report_file.add_line('Going to on-board subsystem - ' + vnf_type)
        onboard_enm_ecm_subsystems('subsystem')


def create_user_so_logviewer_role():
    try:
        log.info('Creating so_logviewer with SO LOGViewer Role ')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_deployment_type = sit_data._SIT__so_deployment_type
        so_host_name = sit_data._SIT__so_host_name
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        user = 'so-user'
        password = 'Ericsson123!'
        tenant = 'master'

        admin_so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, user, password,
                                                            tenant)

        command = '''curl --insecure -X  GET -H 'Cookie: JSESSIONID="{}"' https://{}/idm/usermgmt/v1/users'''.format(
            admin_so_token, so_host_name)

        exists = check_tenant_user_exists(connection, command, 'so_logviewer')

        if not exists:
            Report_file.add_line('Creating so_logviewer with SO LOGViewer Role')

            file_name = 'createLogviewerUser.json'
            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/' + file_name,
                                            SIT.get_base_folder(SIT) + file_name)

            command = '''curl --insecure -X  POST -H "Content-Type: application/json" -H 'Cookie: JSESSIONID="{}"' --data @createLogviewerUser.json https://{}/idm/usermgmt/v1/users'''.format(
                admin_so_token, so_host_name)
            log.info('create so_logviewer with SO LOGViewer Role  ' + command)
            Report_file.add_line('create so_logviewer with SO LOGViewer Role ' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            Report_file.add_line('create so_logviewer with SO LOGViewer Role output ' + command_output)

            verify_user(command_output)

    except Exception as e:

        log.error('Error create so_logviewer with SO LOGViewer Role   ' + str(e))
        Report_file.add_line('Error create so_logviewer with SO LOGViewer Role ' + str(e))
        assert False
    finally:
        connection.close()


def check_so_subsytems():
    try:

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        global so_host_name
        so_deployment_type = sit_data._SIT__so_deployment_type
        so_host_name = sit_data._SIT__so_host_name
        so_entity_check_user = sit_data._SIT__so_entity_check_user
        log.info(f'Checking sub system for user: {so_entity_check_user}')

        if 'so_logviewer' == so_entity_check_user:

            token_user = 'so_logviewer'
            token_password = 'Testing123!!'
            token_tenant = 'master'

        else:

            token_user = 'so-user'
            token_password = 'Ericsson123!'
            token_tenant = 'master'

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)

        command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/subsystem-manager/v1/subsystems'''.format(
            so_token, so_host_name)
        command_output = check_so_user_accessibility('subsystems', connection, command, so_entity_check_user)

        if 'Access Denied' in command_output and 'so_logviewer' == so_entity_check_user:
            log.info('subsystem check command output\n' + command_output)
            log.info('subsystem not listed with so_logviewer user')

        elif 'Access Denied' not in command_output and 'so-user' == so_entity_check_user:
            log.info('subsystem check command output\n' + command_output)
            log.info('subsystem check success')

        else:
            log.error('subsystem check command output\n' + command_output)
            log.error('Not expected output, check above output for details ')
            assert False

    except Exception as e:

        log.error('Error check checking sub system  ' + str(e))
        Report_file.add_line('Error checking sub system ' + str(e))
        assert False
    finally:
        connection.close()


def get_subsystem_loop():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        global so_host_name
        so_deployment_type = sit_data._SIT__so_deployment_type
        so_host_name = sit_data._SIT__so_host_name
        token_user = 'so-user'
        token_password = 'Ericsson123!'
        token_tenant = 'master'

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)

        command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/subsystem-manager/v1/subsystems'''.format(
            so_token, so_host_name)
        while True:
            total_subs, subs_data = check_new_entity_exists('subsystems', connection, command)
            Report_file.add_line('total subsystem  - ' + str(total_subs))
            Report_file.add_line('subsystem data - ' + str(subs_data))
            log.info('total subsystem- ' + str(total_subs))
            log.info('subsystem data - ' + str(subs_data))
            log.info('Waiting 3 seconds to run again..')
            time.sleep(3)
    except Exception as e:

        log.error('Error check checking sub system  ' + str(e))
        Report_file.add_line('Error checking sub system ' + str(e))
        assert False

    finally:

        connection.close()
