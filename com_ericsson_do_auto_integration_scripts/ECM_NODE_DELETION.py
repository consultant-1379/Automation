# pylint: disable=C0301,C0103,C0114,W0703,R1705,W0212,C0116
import ast
import threading
from tabulate import tabulate
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import get_ccm_version
from com_ericsson_do_auto_integration_scripts.PROJ_VIM import get_classic_ecm_version

log = Logger.get_logger('ECM_NODE_DELETION.py')
lock = threading.RLock()
REPORT_TABLE_DATA = []


def print_ecm_terminate_report():
    try:
        lock.acquire()
        log.info('Terminate report for all node packages ')
        Report_file.add_line('Terminate report for all node packages')
        log.info(
            tabulate(
                REPORT_TABLE_DATA,
                headers=["VAPP/NETWORK ID", "VAPP/NETWORK NAME", "VAPP/NETWORK STATUS"],
                tablefmt='grid',
                showindex="always",
            )
        )
        Report_file.add_line(
            tabulate(
                REPORT_TABLE_DATA,
                headers=["VAPP/NETWORK ID", "VAPP/NETWORK NAME", "VAPP/NETWORK STATUS"],
                tablefmt='grid',
                showindex="always",
            )
        )

        for data in REPORT_TABLE_DATA:
            if 'NOT DELETED' in data:
                log.error(
                    'Failure in termination of minimum one node, %s',
                    'please check the above table for more details'
                )
                Report_file.add_line(
                    'Failure in termination of minimum one node ,' +
                    'please check the above table for more details'
                )
                assert False

    except Exception as error:
        log.error('Error termianting nodes from ECM %s', str(error))
        Report_file.add_line('Error termianting nodes from ECM' + str(error))
        assert False
    finally:
        lock.release()


def add_report_data_in_ecm_terminate_report(package_id, package_name, package_status):
    try:
        for data in REPORT_TABLE_DATA:
            if package_id in data:
                return

        report_data = [package_id, package_name, package_status]
        REPORT_TABLE_DATA.append(report_data)

    except Exception as error:
        log.info('Error adding report data in report table :%s', str(error))


def execute_curl_terminate(connection, vapp_dict, token, core_vm_hostname, command):

    try:
        log.info(' Terminating the vApp %s ', vapp_dict)
        vapp_name = vapp_dict['name']
        vapp_id = vapp_dict['id']

        log.info('vApp available %s', vapp_name)
        log.info('vApp id %s', vapp_id)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        output = ast.literal_eval(command_output[2:-1:1])
        request_status = output['status']['reqStatus']

        if 'SUCCESS' in request_status:

            order_id = output.get('correlationId') or output['data']['order']['id']
            log.info('Executed the curl command for termination of vapp: %s', str(vapp_name))
            log.info('CorrelationId (Order id) is : %s', order_id)
            Report_file.add_line('Executed the curl command for termination of vapp: %s' + str(vapp_name))
            Report_file.add_line('CorrelationId (Order id) is : ' + order_id)

            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities, connection, token, core_vm_hostname, order_id, 10
            )
            global REPORT_TABLE_DATA

            if order_status:

                log.info('vApp %s deleted successfully.', str(vapp_name))
                Report_file.add_line('vApp ' + str(vapp_name) + ' deleted successfully. ')
                add_report_data_in_ecm_terminate_report(vapp_id, vapp_name, 'DELETED')

            else:
                Report_file.add_line(order_output)
                log.error('order status for  node termination is errored %s', order_id)
                Report_file.add_line('order status for  node termination is errored  ' + order_id)
                add_report_data_in_ecm_terminate_report(vapp_id, vapp_name, 'NOT DELETED')

        elif 'ERROR' in request_status:

            command_error = output['status']['msgs'][0]['msgText']
            log.error(output['status']['msgs'])
            log.error(
                'Error executing curl command for terminating vapp %s : %s', str(vapp_name), command_error
            )
            Report_file.add_line(
                'Error executing curl command for terminating vapp ' + str(vapp_name) + ": " + command_error
            )
            add_report_data_in_ecm_terminate_report(vapp_id, vapp_name, 'NOT DELETED')

    except Exception as error:
        log.error('Error occured while terminating vapp %s \nERROR: %s', str(vapp_name), str(error))
        Report_file.add_line('Error occured while terminating vapp ' + str(vapp_name) + '\nERROR:' + str(error))
        add_report_data_in_ecm_terminate_report(vapp_id, vapp_name, 'NOT DELETED')

        assert False


def get_vapp_list_from_eocm(connection, token, core_vm_hostname, vnf_type):

    try:
        log.info(' Going to fetch Vapp data for VNF_TYPE %s', vnf_type)
        command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/vapps{}'''.format(
            token, core_vm_hostname, "'"
        )

        log.info('preparing command to fetch vapp list from EO-CM: %s', command)
        Report_file.add_line('preparing command to fetch vapp list from EO-CM: ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        Report_file.add_line('vApp List command_output %s' + command_out)

        output = ast.literal_eval(command_out)
        request_status = output['status']['reqStatus']

        if 'SUCCESS' in request_status:
            if 'data' in output:

                vapps_json = output['data']['vapps']

                if vnf_type == 'ALL':
                    Report_file.add_line(' vApp List {} '.format(vapps_json))
                    return vapps_json
                else:
                    requested_vapps = []
                    for vapp in vapps_json:
                        vapp_name = vapp['name']
                        if vnf_type in vapp_name:
                            requested_vapps.append(vapp)
                    Report_file.add_line(' vApp List {} '.format(requested_vapps))
                    return requested_vapps

            else:

                log.info("No vapps found ")
                return []

        elif 'ERROR' in request_status:

            command_error = output['status']['msgs'][0]['msgText']
            log.error(output['status']['msgs'])
            log.error('Error executing curl command for fetching vapps from EO-CM %s', command_error)
            Report_file.add_line(
                'Error executing curl command for fetching vapps from EO-CM ' + command_error
            )
            connection.close()
            assert False

    except Exception as error:
        connection.close()
        log.error('Error getting vapp list from EO-CM %s', str(error))
        Report_file.add_line('Error getting vapp list from EO-CM ' + str(error))
        connection.close()
        assert False


def terminate_vapp(vnf_type):

    try:

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        vapp_list = get_vapp_list_from_eocm(connection, token, core_vm_hostname, vnf_type)
        network_vapp_list = []
        vapp_count = 1
        thread_pool_vapp = []
        for vapp_dict in vapp_list:

            vapp_name = vapp_dict['name']
            vapp_id = vapp_dict['id']

            log.info('generating curl command for terminating vapp %s', vapp_name)

            if 'ECDE' in vapp_name or 'Network' in vapp_name or 'EOST' in vapp_name:

                network_vapp_list.append(vapp_dict)

            else:

                if 'TOSCA_DUMMY' in vapp_name:
                    terminate_file_name = "terminate_tosca_dummy_node.json"
                else:
                    terminate_file_name = "terminate_node.json"

                log.info('Transferring %s on ECM Host blade', terminate_file_name)

                ServerConnection.put_file_sftp(
                    connection,
                    f'com_ericsson_do_auto_integration_files/{terminate_file_name}',
                    f'{SIT.get_base_folder(SIT)}{terminate_file_name}')


                if 'MIP_PORT_SOL_VBGF' in vapp_name:

                    command = '''curl -X DELETE --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/vapps/{}{}'''.format(
                        token, core_vm_hostname, vapp_id, "'"
                    )

                else:

                    command = '''curl -X DELETE --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} 'https://{}/ecm_service/v2/vapps/{}/terminate{}'''.format(
                        token, terminate_file_name, core_vm_hostname, vapp_id, "'"
                    )

                Report_file.add_line('Curl command for terminating vapp ' + command)
                log.info('Curl command for terminating vapp %s', command)
                thread = threading.Thread(
                    target=execute_curl_terminate,
                    name='Thread_' + str(vapp_count),
                    args=(connection, vapp_dict, token, core_vm_hostname, command),
                )
                thread_pool_vapp.append(thread)
                vapp_count = vapp_count + 1

        for task in thread_pool_vapp:
            task.start()
        for task in thread_pool_vapp:
            task.join()

        thread_pool_network_vapp = []
        network_vapp_count = 1
        for network_vapp_dict in network_vapp_list:

            vapp_network_id = network_vapp_dict['id']

            command = '''curl -X DELETE --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/vapps/{}{}'''.format(
                token, core_vm_hostname, vapp_network_id, "'"
            )

            Report_file.add_line('Curl command for terminating vapp network ' + command)
            log.info('Curl command for terminating vapp network %s', command)
            thread = threading.Thread(
                target=execute_curl_terminate,
                name='Thread_' + str(network_vapp_count),
                args=(connection, network_vapp_dict, token, core_vm_hostname, command),
            )
            thread_pool_network_vapp.append(thread)
            network_vapp_count = network_vapp_count + 1

        for task in thread_pool_network_vapp:
            task.start()
        for task in thread_pool_network_vapp:
            task.join()

    except Exception as error:
        log.error('Error in preparing curl command for terminating the vapp \nERROR: %s', str(error))
        Report_file.add_line('Error in preparing curl command for terminating the vapp \nERROR: ' + str(error))
        assert False

    finally:
        connection.close()


def execute_curl_network_terminate(connection, network_dict, token, core_vm_hostname):

    try:
        log.info(' Network details  %s ', network_dict)
        network_name = network_dict['name']
        network_id = network_dict['id']

        log.info('network available %s', network_name)
        log.info('Network id %s', network_id)

        if 'EOST' in network_name:

            log.info('generating curl command for terminating network %s', network_name)
            command = '''curl -X DELETE --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/v2/vns/{}{}'''.format(
                token, core_vm_hostname, network_id, "'"
            )

            Report_file.add_line('Curl command for terminating network ' + command)
            log.info('Curl command for terminating network %s', command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            log.info('Executed curl command to terminate network')
            Report_file.add_line('Executed curl command to terminate network')
            output = ast.literal_eval(command_output[2:-1:1])
            request_status = output['status']['reqStatus']

            if 'SUCCESS' in request_status:
                order_id = output['data']['order']['id']
                log.info('Executed the curl command for termination of network: %s', str(network_name))
                log.info('Order is : %s', order_id)
                Report_file.add_line(
                    'Executed the curl command for termination of network: ' + str(network_name)
                )
                Report_file.add_line('Order id is : ' + order_id)

                order_status, order_output = Common_utilities.orderReqStatus(
                    Common_utilities, connection, token, core_vm_hostname, order_id, 10
                )

                if order_status:
                    log.info('network %s deleted successfully.', str(network_name))
                    Report_file.add_line('network ' + str(network_name) + ' deleted successfully. ')
                    add_report_data_in_ecm_terminate_report(network_id, network_name, 'DELETED')

                else:
                    Report_file.add_line(order_output)
                    log.error('order status for network termination is errored %s', order_id)
                    Report_file.add_line('order status for network termination is errored  ' + order_id)
                    add_report_data_in_ecm_terminate_report(network_id, network_name, 'NOT DELETED')

            elif 'ERROR' in request_status:

                command_error = output['status']['msgs'][0]['msgText']
                log.error(output['status']['msgs'])
                log.error(
                    'Error executing curl command for terminating network %s :%s',
                    str(network_name),
                    command_error
                )
                Report_file.add_line(
                    'Error executing curl command for terminating network '
                    + str(network_name)
                    + ": "
                    + command_error
                )
                add_report_data_in_ecm_terminate_report(network_id, network_name, 'NOT DELETED')

        else:
            log.info('Networks are not for EOST GVNM')

    except Exception as error:
        log.error('Error occurred while terminating network %s \nERROR: %s', str(network_name), str(error))
        Report_file.add_line(
            'Error occurred while terminating network ' + str(network_name) + '\nERROR:' + str(error)
        )
        add_report_data_in_ecm_terminate_report(network_id, network_name, 'NOT DELETED')
        assert False


def get_network_list_from_eocm(connection, token, core_vm_hostname, is_cloud_native=False):

    try:
        if is_cloud_native:
            ecm_verison = get_ccm_version(connection, token, core_vm_hostname, '1.15.0-92')
            if ecm_verison:
                command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/v2/vns{}'''.format(
                    token, core_vm_hostname, "'"
                )
            else:
                command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/vns{}'''.format(
                    token, core_vm_hostname, "'"
                )
        else:
            ecm_verison = get_classic_ecm_version(connection, core_vm_hostname, '20.7.1.0.2214.2638')
            if ecm_verison:
                command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/v2/vns{}'''.format(
                    token, core_vm_hostname, "'"
                )
            else:
                command = '''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/vns{}'''.format(
                    token, core_vm_hostname, "'"
                )

        log.info('preparing command to fetch network list from EO-CM: %s', command)
        Report_file.add_line('preparing command to fetch network list from EO-CM: ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)
        request_status = output['status']['reqStatus']

        if 'SUCCESS' in request_status:

            if 'data' in output:
                network_json = output['data']['vns']
                Report_file.add_line(' network List {} '.format(network_json))
                return network_json

            else:
                log.info("No network found ")
                return []

        elif 'ERROR' in request_status:

            command_error = output['status']['msgs'][0]['msgText']
            log.error(output['status']['msgs'])
            log.error('Error executing curl command for fetching network from EO-CM %s', command_error)
            Report_file.add_line(
                'Error executing curl command for fetching network from EO-CM ' + command_error
            )
            connection.close()
            assert False

    except Exception as error:
        connection.close()
        log.error('Error getting network list from EO-CM %s', str(error))
        Report_file.add_line('Error getting network list from EO-CM ' + str(error))
        connection.close()
        assert False


def terminate_network():

    try:

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        is_cloud_native = ecm_host_data.get_is_cloudnative(ecm_host_data)
        network_list = get_network_list_from_eocm(connection, token, core_vm_hostname, is_cloud_native)
        count = 1
        thread_pool = []
        for network_dict in network_list:
            thread = threading.Thread(
                target=execute_curl_network_terminate,
                name='Thread_' + str(count),
                args=(connection, network_dict, token, core_vm_hostname),
            )
            thread_pool.append(thread)
            count = count + 1

        for task in thread_pool:
            task.start()
        for task in thread_pool:
            task.join()

    except Exception as error:
        log.error('Error in preparing curl command for terminating the network \nERROR: %s', str(error))
        Report_file.add_line('Error in preparing curl command for terminating the network \nERROR: ' + str(error))
        assert False

    finally:
        connection.close()


def start_ecm_node_deletion():
    log.info('Starting script : ECM Node and Network deletion ')
    Report_file.add_line('Starting script : ECM Node and Network deletion ')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnf_type = sit_data._SIT__vnf_type
    log.info('Going to terminate VNF_TYPE %s', vnf_type)
    terminate_vapp(vnf_type)

    if vnf_type == 'ALL':
        terminate_network()

    print_ecm_terminate_report()

    log.info('END script : ECM Node and Network deletion ')
    Report_file.add_line('END script : ECM Node and Network deletion ')
