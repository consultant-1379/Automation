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
import ast
from com_ericsson_do_auto_integration_initilization.Initialization_script import \
    Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import \
    ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.General_files_update import update_register_cism, \
    update_modify_cism
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_scripts.EVNFM_NODE_DEPLOYMENT import \
    upload_node_ccd_target_cnfig
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.EPIS import EPIS

log = Logger.get_logger('CISM_ZONE_CLUSTER.py')


def register_cism_zone():
    try:

        log.info('Start to register CISM Zone Cluster')
        Report_file.add_line('Start to register CISM Zone Cluster ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        directory_server_ip = ecm_host_data._Ecm_core__cism_cluster_ip
        directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        register_url = ecm_host_data._Ecm_core__cism_register_url
        tenant_id = EPIS_data._EPIS__tenant_name
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

        file_path = 'eccd-2-3.pem'

        config_file_path = f'/home/{directory_server_username}/.kube/config'

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        nested_conn = ServerConnection.get_nested_server_connection(connection, ecm_server_ip, directory_server_ip,
                                                                    directory_server_username, file_path)

        log.info('fetching config file to get encoded certificate and key ')
        ServerConnection.get_file_sftp(nested_conn, config_file_path, 'config')

        if is_cloudnative:
            file_name = 'CN_Register_CISM.json'
        else:
            file_name = 'Register_CISM.json'

        update_register_cism(file_name, nested_conn, register_url)

        log.info('Transferring register_cism.json file to director server ip ' + directory_server_ip)
        ServerConnection.put_file_sftp(nested_conn, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       r'/home/' + directory_server_username + '/' + file_name)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('Register CISM Zone with curl command  ')

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'tenantid:{}' --header 'AuthToken: {}' --data @{} 'https://{}/ecm_service/cisms{}'''.format(
            tenant_id, token, file_name, core_vm_hostname, "'")

        Report_file.add_line('register cism zone command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(nested_conn, command)

        Report_file.add_line('register command output : ' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 10)

            if order_status:

                log.info('CISM Register Order Status is completed ' + order_id)
                Report_file.add_line('CISM Register Order Status is completed ' + order_id)
                log.info('CISM ZONR Registered successfully.')
                Report_file.add_line('CISM ZONR Registered successfully.')

            else:

                log.info(order_output)
                log.error('CISM Register Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('CISM Register Order Status is failed with message mentioned above ' + order_id)
                assert False


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for registering CISM Zone ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for registering CISM Zone')
            assert False


    except Exception as e:
        log.error('Error registering CISM Zone Cluster ' + str(e))
        Report_file.add_line('Error registering CISM Zone Cluster ' + str(e))
        assert False

    finally:
        connection.close()


def get_registered_cism_id(nested_conn, tenant_id, token, core_vm_hostname):
    try:
        log.info('Getting registered cism id')

        command = '''curl --insecure --location --request GET --header 'Content-Type: application/json' --header 'tenantid:{}' --header 'AuthToken: {}' 'https://{}/ecm_service/cisms?$filter=tenantName%3D{}{}'''.format(
            tenant_id, token, core_vm_hostname, tenant_id, "'")

        Report_file.add_line('register cism zone command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(nested_conn, command)

        Report_file.add_line('register command output : ' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            if "data" not in output:
                log.info('CISM is Not Registered')
                Report_file.add_line('CISM is Not Registered')
                registered_cisms_id = 'NOT_REGISTERED'
            else:
                registered_cisms_id = output['data']['cisms'][0]['id']
                log.info('CISM Registered id ' + registered_cisms_id)
                Report_file.add_line('CISM Registered id ' + registered_cisms_id)
            return registered_cisms_id


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for getting registered CISM ID ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for getting registered CISM id')
            assert False


    except Exception as e:

        log.error('Error getting registered cism id ' + str(e))
        Report_file.add_line('Error getting registered cism id')


def derigester_cism_zone():
    try:

        log.info('Start to de-register CISM Zone Cluster')
        Report_file.add_line('Start to de-register CISM Zone Cluster ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        directory_server_ip = ecm_host_data._Ecm_core__cism_cluster_ip
        directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        tenant_id = EPIS_data._EPIS__tenant_name

        file_path = 'eccd-2-3.pem'

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        nested_conn = ServerConnection.get_nested_server_connection(connection, ecm_server_ip, directory_server_ip,
                                                                    directory_server_username, file_path)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        registered_cisms_id = get_registered_cism_id(nested_conn, tenant_id, token, core_vm_hostname)

        if registered_cisms_id == 'NOT_REGISTERED':
            log.info('CISM NOT REGISTERED. HENCE PASSING THE DE-REGISTER JOB')
            Report_file.add_line('CISM NOT REGISTERED. HENCE PASSING THE DE-REGISTER JOB')
            return True

        log.info('De-register CISM Zone with curl command ')

        command = '''curl --insecure 'https://{}/ecm_service/cisms/{}' -X DELETE -H 'Accept: application/json' -H 'AuthToken: {}{}'''.format(
            core_vm_hostname, registered_cisms_id, token, "'")

        Report_file.add_line('de-register cism zone command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(nested_conn, command)

        Report_file.add_line('de-register command output : ' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 10)

            if order_status:

                log.info('CISM de-register Order Status is completed ' + order_id)
                Report_file.add_line('CISM de-register Order Status is completed ' + order_id)
                log.info('CISM ZONR de-registered successfully.')
                Report_file.add_line('CISM ZONR de-registered successfully.')

            else:

                log.info(order_output)
                log.error('CISM de-register Order Status is failed with message mentioned above ' + order_id)
                Report_file.add_line('CISM de-register Order Status is failed with message mentioned above ' + order_id)
                assert False


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for de-registering CISM Zone ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for de-registering CISM Zone')
            assert False


    except Exception as e:
        log.error('Error de-registering CISM Zone Cluster ' + str(e))
        Report_file.add_line('Error de-registering CISM Zone Cluster ' + str(e))
        assert False

    finally:
        connection.close()


def check_cism_register_exits(connection, evnfm_token, evnfm_hostname, file_name):
    log.info('Start checking if  cism register from EVNFM is exists or not ')

    command = f'''curl --insecure -X GET -H 'Accept: */*' -H 'cookie: JSESSIONID="{evnfm_token}"' https://{evnfm_hostname}/vnflcm/v1/clusterconfigs'''
    log.info('Command to list out clusters: %s', command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    log.info('Command output of above command: %s', command_output)

    if '"error":"Not Found"' in command_output:
        log.error('This end point does not exists , move to old API')
        return "RUN_OLD_API", ''

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    output = ast.literal_eval(command_out)

    items = output['items']

    for item in items:
        name = item['name']
        default_flag = item['isDefault']
        if file_name == name:
            log.info('CISM Register exists in EVNFM')
            return True, default_flag

    log.info('CISM Register does not exist in EVNFM')
    return False, ''


def register_evnfm_cism_zone():
    try:

        log.info('Start registering cism from EVNFM ')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        file_name = SIT.get_cluster_config_file(SIT)
        software_dir = '/var/tmp/deployCCRC/'

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        for file in file_name.split(','):
            cism_exists, is_default = check_cism_register_exits(connection, evnfm_token, evnfm_hostname, file)

            if cism_exists:
                log.info('Already registered cism from EVNFM')
                log.info('Default cluster: %s', is_default)
            elif 'RUN_OLD_API' == cism_exists:

                upload_node_ccd_target_cnfig('CCRC_CNF', file, software_dir)

            else:
                curl = '''curl -i --insecure -X POST https://{}/vnflcm/v1/clusterconfigs -H 'Accept: */*' -H 'cookie: JSESSIONID={}' -F clusterConfig=@{}'''.format(
                    evnfm_hostname, evnfm_token, file)
                log.info('Curl command to register cluster: %s', curl)
                command = 'cd ' + software_dir + ' ; ' + curl

                command_output = ExecuteCurlCommand.get_json_output(connection, command)
                log.info('Cluster registeration command output: %s', command_output)

                if '201 Created' in command_output:
                    log.info('Finished registering cism from EVNFM ')
                    log.info('Default cluster: %s', is_default)

                else:
                    log.error('Error registering cism from EVNFM  , check logs for details')
                    assert False

    except Exception as e:

        log.error('Error registering cism from EVNFM ' + str(e))
        assert False
    finally:
        connection.close()


def deregister_evnfm_cism_zone():
    try:

        log.info('Start de-registering cism from EVNFM ')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        file_name = SIT.get_cluster_config_file(SIT)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        for file in file_name.split(','):
            cism_exists, is_default = check_cism_register_exits(connection, evnfm_token, evnfm_hostname, file)

            if cism_exists and is_default == False:

                command = f'''curl --insecure -i -X DELETE https://{evnfm_hostname}/vnflcm/v1/clusterconfigs/{file} -H 'Accept: */*' -H 'cookie: JSESSIONID="{evnfm_token}"{"'"}'''
                log.info('Command to delete the cluster: %s', command)

                command_output = ExecuteCurlCommand.get_json_output(connection, command)
                log.info('Command output: %s', command_output)

                if '204 No Content' in command_output:
                    log.info('Finished de-registering cism from EVNFM ')

                else:
                    log.error('Error de-registering cism from EVNFM  , check logs for details')
                    assert False
            elif 'RUN_OLD_API' == cism_exists:
                log.info('Nothing to do here , ENV supports the old API . Please check ')

            else:
                log.info('Already de-registered cism from EVNFM ')


    except Exception as e:

        log.error('Error de-registering cism from EVNFM ' + str(e))
        assert False
    finally:
        connection.close()


def modify_cism_zone():
    connection = None
    try:
        log.info('Start to modify CISM Zone Cluster')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        tenant_name = EPIS.get_tenant_name(EPIS)
        register_url = Ecm_core.get_cism_register_url(Ecm_core)

        file_name = 'modify_register_CISM.json'

        update_modify_cism(file_name, register_url)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Transferring modify_register_cism.json file to blade %s', ecm_server_ip)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        registered_cisms_id = get_registered_cism_id(connection, tenant_name, token, core_vm_hostname)

        if registered_cisms_id == 'NOT_REGISTERED':
            log.info('CISM NOT REGISTERED. HENCE PASSING THE MODIFY CISMS JOB')
            return True

        log.info('Modify CISM Zone with curl command  ')

        curl_command = f'curl -X PATCH --insecure  ' \
                       f'https://{core_vm_hostname}/ecm_service/cisms/{registered_cisms_id} ' \
                       f'-H "Content-Type: application/json" ' \
                       f'-H "AuthToken: {token}"' \
                       f' --data @{file_name}'

        output = Common_utilities.execute_curl_command(Common_utilities, connection, curl_command)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, order_id, 10)

            if order_status:
                log.info('CISM Modify Order Status is completed %s', order_id)
            else:
                log.info(order_output)
                log.error('CISM modify Order Status is failed with message mentioned above %s', order_id)
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for modifying CISM Zone %s', command_error)
            assert False


    except Exception as e:
        log.error('Error modifying CISM Zone Cluster %s', str(e))
        assert False

    finally:
        if connection:
            connection.close()
