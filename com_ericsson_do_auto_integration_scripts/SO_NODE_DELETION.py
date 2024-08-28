# pylint: disable=C0302,C0103,C0301,W0614,C0412,W0212,C0411
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
"""
Created on 25 Apr 2019
@author: emaidns
"""

import ast
import time
from tabulate import tabulate
import threading
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.SO_file_update import update_service_delete_file
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import (
    get_VMVNFM_host_connection, transfer_director_file_to_vm_vnfm, get_master_vnflcm_db_pod, fetch_vmvnfm_version
)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import fetch_so_version
from packaging import version

log = Logger.get_logger('SO_NODE_DELETION.py')

lock = threading.RLock()
report_table_data = []


def check_terminate_state_network_service(connection, command, service_id):
    """
    @param connection: connection object
    @param command: command to be executed
    @param service_id: numeric id of service to terminate
    """
    try:
        lock.acquire()
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        if f"Service with id {service_id} does not exist" in output.values() or 'does not exist' in output.values():
            return "Not Found", output

        return output['state'], output

    except Exception as e:
        log.error('Error getting the terminate state from SO  %s', str(e))
        Report_file.add_line('Error getting the terminate state from SO ' + str(e))
        assert False
    finally:
        lock.release()


def print_terminate_report():
    """
    Print report
    """
    try:
        lock.acquire()
        log.info('Terminate report for all node packages ')
        Report_file.add_line('Terminate report for all node packages')
        log.info(tabulate(report_table_data,
                          headers=["SERVICE ID", "PACKAGE NAME", "SO SERVICE STATUS", "ECM ORDER STATUS",
                                   "LCM WORKFLOW STATUS"], tablefmt='grid',
                          showindex="always"))
        Report_file.add_line(tabulate(report_table_data,
                                      headers=["SERVICE ID", "PACKAGE NAME", "SO SERVICE STATUS", "ECM ORDER STATUS",
                                               "LCM WORKFLOW STATUS"],
                                      tablefmt='grid', showindex="always"))

        for data in report_table_data:
            if 'FAIL' in data:
                log.error('Failure in termination of minimum one node , please check the above table for more details')
                Report_file.add_line('Failure in termination of minimum one node , please check the above table for more details')
                assert False

    except Exception as e:
        log.error('Error termianting nodes from SO %a', str(e))
        Report_file.add_line('Error termianting nodes from SO %s', str(e))
        assert False
    finally:
        lock.release()


def change_db_passwd_when_permission_denied(interact, password):
    """
    CHange db password
    @param interact: Channel connected to the remote shell
    @param password: new password
    """
    log.info('Start to reset the vnflcm password from default to given on DIT')
    interact.send('passw0rd' + '\n')
    time.sleep(5)
    resp = interact.recv(9999)
    buff = str(resp)
    log.info(buff)

    if 'UNIX password' in buff:
        interact.send('passw0rd' + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

    if 'New password:' in buff:
        interact.send(password + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

    if 'Retype new password' in buff:
        interact.send(password + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

    log.info('End reset the vnflcm password from default to given on DIT')

    if 'Connection to vnflaf-db closed' in buff:
        # connect with LCM DB
        command = 'sshdb'
        interact.send(command + '\n')
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if "vnflaf-db's password" in buff:
            interact.send(password + '\n')
            time.sleep(4)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

            if 'Permission denied' in buff:
                # same has to update in multiple places when pushing the code
                log.error('Permission denied again after password change of DB VM. Please check on LCM DB VM.')
                assert False

    else:
        log.error('Connection from vnflaf-db not closed after DB VM password change')
        assert False


def check_terminate_lcm_workflow_status(node_package_name, node_defination_name):
    """
    @param node_package_name:
    @param node_defination_name:
    @return:
    """
    try:
        lock.acquire()

        log.info('Start to check lcm_workflow_status for %s', node_package_name)
        Report_file.add_line('Start to check lcm_workflow_status for ' + node_package_name)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        if 'VNFM' in node_package_name or 'TRUE' == is_vm_vnfm:
            connection = get_VMVNFM_host_connection()
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
                command = 'psql -U postgres -d wfsdb'
            else:
                if 'postgres@' not in buff:
                    command = 'su postgres'
                    interact.send(command + '\n')
                    time.sleep(3)
                    resp = interact.recv(9999)
                    buff = str(resp)
                    log.info(buff)
                command = 'psql -d wfsdb'
            interact.send(command + '\n')
            time.sleep(3)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)


        else:

            connection = ServerConnection.get_connection(server_ip, username, password)
            interact = connection.invoke_shell()

            command = 'sudo -i'
            interact.send(command + '\n')
            time.sleep(2)

            command = 'sshdb'
            interact.send(command + '\n')

            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

            if "vnflaf-db's password" in buff:
                interact.send(password + '\n')
                time.sleep(4)
                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                if 'Permission denied' in buff:
                    log.info('Permission denied , password has been changed . Going to set it again')
                    change_db_passwd_when_permission_denied(interact, password)

            command = 'sudo -u postgres psql'
            interact.send(command + '\n')
            time.sleep(2)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'postgres=' in buff:
                command = '\c wfsdb'
                interact.send(command + '\n')
                time.sleep(2)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

        if 'wfsdb=' in buff:
            command = '''select businesskey,definitionname,lastpnodeid,endnodeid from workflowprogresssummary WHERE businesskey LIKE '{}%' AND definitionname ='{}';'''.format(
                node_package_name, node_defination_name)
            interact.send(command + '\n')
            time.sleep(3)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        interact.shutdown(2)

        if '(0 rows)' in buff:
            log.info('No record found for requested node package name')
            log.info('terminate workflow not found please check the node package name')
            return 'NOT FOUND'
        else:
            index = buff.index(node_package_name + '_')
            new_string = buff[index:]
            data_list = new_string.split('|')

            if 'End__prg__p100' in data_list[2] and 'End__prg__p100' in data_list[3]:
                log.info(
                    'terminate workflow is successfully completed with lastpnodeid and endnodeid as End__prg__p100  %s',
                    node_package_name)
                Report_file.add_line('terminate workflow is successfully completed with lastpnodeid and endnodeid as End__prg__p100 ' + node_package_name)
                return 'PASS'

            else:
                log.error('some faliure at very end of node terminate lastpnodeid is %s',
                          data_list[2] + 'and endnodeid is %s', data_list[3])
                Report_file.add_line('some faliure at very end of node terminate lastpnodeid is ' + data_list[
                                         2] + 'and endnodeid is ' + data_list[3])
                return 'FAIL'


    except Exception as e:
        log.error('Exception occured details : %s', str(e))
        log.error('Error to check lcm_workflow_status for %s', node_package_name)
        Report_file.add_line('Error to check lcm_workflow_status for ' + node_package_name)
        assert False
    finally:
        connection.close()
        lock.release()


def check_terminate_ecm_order_status(node_package_name):
    """
    Check and return the service terminate order status
    @param node_package_name:
    @return: order status
    """
    try:
        lock.acquire()
        log.info('Start to check ECM order status for %s', node_package_name)
        Report_file.add_line('Start to check ECM order status for ' + node_package_name)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        command = '''curl --insecure -X GET --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/orders?$filter=searchTag%3DVAPP%7C{}{}'''.format(
            token, core_vm_hostname, node_package_name, "'")

        Report_file.add_line('Curl command for getting ECM order number and status ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            if 'data' in output.keys() and output['data']:
                order_id = output['data']['orders'][0]['id']
                log.info(f'order id for {node_package_name} in ECM {order_id}')
                Report_file.add_line('order id for ' + node_package_name + ' in ECM ' + order_id)
                order_status = output['data']['orders'][0]['orderReqStatus']
                log.info('ECM order status is %s', order_status)
                if 'COM' in order_status or 'WARN' in order_status:

                    log.info('Order status for order id %s is completed with status %s', order_id, order_status)
                    Report_file.add_line('Order status for order id ' + order_id + ' is completed with status ' + order_status)

                    return 'PASS'

                elif 'ERR' in order_status:
                    log.error('Order Status is failed %s', order_id)
                    Report_file.add_line('Order Status is failed ' + order_id)
                    return 'FAIL'
                else:
                    log.info('Order Status is still in progress %s', order_id)
                    Report_file.add_line('Order Status is still in progress ' + order_id)
                    return 'FAIL-IN_PROGRESS'

            else:
                log.info(
                    'Order not found in ECM , Reason : check the network service name, it should match the node package name')
                Report_file.add_line('Order not found in ECM , Reason : check the network service name, it should match the node package name')
                return 'NOT FOUND'


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command check ECM order status %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command check ECM order status')
            assert False

    except Exception as e:
        log.error('Error to check ECM order status for %s : %s', node_package_name, str(e))
        Report_file.add_line('Error to check ECM order status for ' + node_package_name)
        assert False
    finally:
        connection.close()
        lock.release()


def check_so_terminate_service_state(timeout, service_id, connection, so_token, delete_id):
    """
    @param timeout: timeout in seconds
    @param service_id: numeric value
    @param connection: connection object
    @param so_token: token
    @return:
    """
    try:

        log.info('start polling network Service state on the basis of service id ')
        Report_file.add_line('polling network Service state on the basis of service id begins...')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        so_host_name = sit_data._SIT__so_host_name

        log.info('Waiting 10 seconds to kickoff the terminate from SO')
        time.sleep(10)

        log.info('Polling SO network service using the token for authentication and Service Id %s', service_id)

        Report_file.add_line('Polling SO network service using the token for authentication and Service Id ' + service_id)
        log.info('time out for this process is 20 mins')
        timeout = 1200

        if so_version >= version.parse('2.11.0-118'):
            log.info('Polling SO network for Delete Id %s', delete_id)
            Report_file.add_line('Polling SO network for Delete Id -' + delete_id)

            command = f'''curl --insecure -H 'Cookie: JSESSIONID="{so_token}"' 'https://{so_host_name}/service-order-mgmt/v1/serviceOrder/{delete_id}{"'"}'''

        else:

            command = f'''curl --insecure -H 'Cookie: JSESSIONID="{so_token}"' 'https://{so_host_name}/orchestration/v1/services/{service_id}{"'"}'''

        log.info(command)
        Report_file.add_line('command :' + command)
        active_retry = 0
        counter = 0
        while timeout != 0:

            state, output_data = check_terminate_state_network_service(connection, command, service_id)

            if so_version >= version.parse('2.11.0-118'):

                if 'assessing' in state:
                    counter += 1
                    if counter > 2:
                        log.error('Network service termination status is Assessing for service id %s', service_id)
                        Report_file.add_line('Network service termination status is Assessing for service id %s',
                                             service_id)
                        assert False
                    else:
                        log.info('Network service termination status is Assessing for service id %s', service_id)
                        Report_file.add_line(
                            'Network service termination status is Assessing for service id ' + service_id)
                        log.info('waiting 30 seconds to check again the state')
                        timeout = timeout - 30
                        time.sleep(30)

                elif 'acknowledged' in state or 'inProgress' in state:
                    log.info('Network service termination is in progress for service id %s', service_id)
                    Report_file.add_line('Network service termination is in progress for service id ' + service_id)
                    log.info('waiting 60 seconds to check again the state')
                    timeout = timeout - 60
                    time.sleep(60)
                elif 'completed' in state:
                    log.info(f'Network service termination order status is completed for service id {service_id}')
                    Report_file.add_line(f'Network service termination order status is completed for service id {service_id}')

                    log.info('Checking Network service state and service order item state')

                    service_order_item_state = output_data['serviceOrderItem'][0]['state']
                    service_state = output_data['serviceOrderItem'][0]['service']['state']

                    log.info(
                        f'Network service order item is {service_order_item_state} and service state is {service_state} ')
                    Report_file.add_line(f'Network service order item is {service_order_item_state} and service state is {service_state} ')

                    if service_order_item_state == "completed" and service_state == "terminated":
                        log.info(f'Network service termination successfully completed for {service_id}')
                        Report_file.add_line('Network service termination successfully completed ')
                        return 'PASS'

                    else:
                        log.error('network service termination failed , please check the above logs for states')
                        Report_file.add_line('network service termination failed , please check the above logs for states')
                        return 'FAIL'

                else:
                    log.error('network service termination failed state is  %s', state)
                    Report_file.add_line('network service termination failed state is  ' + state)
                    return 'FAIL'

            else:
                if 'InProgress' in state:
                    log.info('Network service termination is in progress for service id %s', service_id)
                    Report_file.add_line('Network service termination is in progress for service id ' + service_id)
                    log.info('waiting 60 seconds to check again the state')
                    timeout = timeout - 60
                    time.sleep(60)
                elif 'Not Found' in state:
                    log.info('Network service termination successfully completed')
                    Report_file.add_line('Network service termination successfully completed')
                    return 'PASS'
                elif 'Errored' in state:
                    log.error('network service termination failed with state %s', state)
                    Report_file.add_line('network service termination failed with state ' + state)
                    return 'FAIL'
                else:
                    if "Active" in state and active_retry == 0:
                        log.info('Network Service termination not started state is  %s', state)
                        log.info('waiting 30 seconds to check again the state')
                        active_retry = 1
                        time.sleep(30)
                    else:
                        log.error('Network Service termination not started state is  %s', state)
                        Report_file.add_line('Network Service termination not started state is  ' + state)
                        return 'FAIL'

        if timeout == 0:
            log.info('Automation script timed out after 20 minutes, Network Service state : %s', state)
            Report_file.add_line('Automation script timed out after 20 minutes, Network Service state : ' + state)
            return 'FAIL'

    except Exception as e:
        log.info('Error checking in SO terminate status for service id %s : %s', service_id, str(e))
        Report_file.add_line('Error checking in SO terminate status for service id ' + service_id)
        assert False

    finally:
        connection.close()


def work_thread(service_id, package_name, connection, so_token, delete_id):
    """
    @param service_id:
    @param package_name:
    @param connection:
    @param so_token:
    """
    try:
        log.info('Starting service termination for service id %s', service_id)
        Report_file.add_line('Starting service termination for service id ' + service_id)
        so_status = check_so_terminate_service_state(1200, service_id, connection, so_token, delete_id)
        ecm_order_status = check_terminate_ecm_order_status(package_name)
        lcm_workflow_status = check_terminate_lcm_workflow_status(package_name, 'Finalize Termination')
        report_data = [service_id, package_name, so_status, ecm_order_status, lcm_workflow_status]
        global report_table_data
        report_table_data.append(report_data)
        log.info('Finished service termination for service id %s', service_id)
        Report_file.add_line('Finished service termination for service id ' + service_id)

    except Exception as e:
        log.error('Error %s', str(e))
        log.error('Error service termination for service id %s', service_id)
        Report_file.add_line('Error service termination for service id ' + service_id)
        assert False


def start_so_node_deletion():
    """Deletes SO service"""

    log.info('Starting script : SO Network service deletion')
    Report_file.add_line('Starting script : SO Network service deletion')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    so_host_name = sit_data._SIT__so_host_name
    vnf_type = sit_data._SIT__vnf_type
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    so_deployment_type = sit_data._SIT__so_deployment_type
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password

    global so_version
    so_version = fetch_so_version('ALL')
    service_delete_file = 'delete_service.json'
    service_names_list = list(vnf_type.split(","))
    log.info('Service names list from VNF-TYPE : ')
    log.info(service_names_list)

    if so_deployment_type == 'IPV6':

        log.info('SO Deployment type is IPV6, connecting with open stack ')
        connection = ServerConnection.get_connection(openstack_ip, username, password)

    else:
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    token_user = 'staging-user'
    token_password = 'Testing12345!!'
    token_tenant = 'staging-tenant'

    so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                  token_password, token_tenant)

    command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/orchestration/v1/services'''.format(
        so_token,
        so_host_name)
    Report_file.add_line('command :' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    connection.close()
    output = ast.literal_eval(command_out)
    active = 0
    thread_pool = []
    log.info(output)

    if len(output) > 0:
        if 'ALL' in service_names_list:
            log.info('Terminating all the active so services')
            for item in output:
                if item['state'] == 'Active':
                    active += 1
                    service_id = item['id']
                    service_name = item['name']

                    if so_deployment_type == 'IPV6':

                        log.info('SO Deployment type is IPV6, connecting with open stack ')
                        connection = ServerConnection.get_connection(openstack_ip, username,
                                                                     password)

                    else:
                        connection = ServerConnection.get_thread_connection(ecm_server_ip,
                                                                            ecm_username, ecm_password)

                    so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name,
                                                                  token_user, token_password, token_tenant)
                    log.info('termination starts for service: %s', str(service_name))

                    if so_version < version.parse('2.11.0-118'):

                        command = '''curl -X DELETE --insecure 'https://{}/orchestration/v1/services/{}' -H 'Cookie: JSESSIONID="{}"{}'''.format(
                            so_host_name, service_id, so_token, "'")
                    else:
                        update_service_delete_file(service_delete_file, service_id, service_name)
                        ServerConnection.put_file_sftp(connection,
                                                       r'com_ericsson_do_auto_integration_files/' + service_delete_file,
                                                       SIT.get_base_folder(SIT) + service_delete_file)
                        command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={so_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d @{service_delete_file} https://{so_host_name}/service-order-mgmt/v1/serviceOrder'''

                    log.info("Curl command : %s", command)
                    Report_file.add_line("Curl command :" + command)

                    command_output = ExecuteCurlCommand.get_json_output(connection,
                                                                        command)
                    log.info("Command output: %s", command_output)
                    Report_file.add_line("Command output: " + command_output)

                    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
                    output = ast.literal_eval(command_out)
                    delete_id = output['id']
                    log.info("service delete id: %s", delete_id)
                    Report_file.add_line("service delete id: " + delete_id)

                    thread = threading.Thread(target=work_thread, name='Thread_' + str(active),
                                              args=(service_id, service_name, connection, so_token, delete_id))
                    thread_pool.append(thread)

        else:
            for so_service_name in service_names_list:
                for item in output:
                    if item['state'] == 'Active':
                        active += 1
                        if so_service_name in item['name']:
                            log.info('Terminating so service : %s', str(so_service_name))
                            service_id = item['id']
                            service_name = item['name']

                            if so_deployment_type == 'IPV6':
                                log.info('SO Deployment type is IPV6, connecting with open stack ')
                                connection = ServerConnection.get_connection(openstack_ip, username,
                                                                             password)
                            else:
                                connection = ServerConnection.get_thread_connection(ecm_server_ip,
                                                                                    ecm_username, ecm_password)

                            so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name,
                                                                          token_user, token_password, token_tenant)
                            log.info('termination starts for service: %s', str(service_name))

                            if so_version < version.parse('2.11.0-118'):
                                command = '''curl -X DELETE --insecure 'https://{}/orchestration/v1/services/{}' -H 'Cookie: JSESSIONID="{}"{}'''.format(
                                    so_host_name, service_id, so_token, "'")

                            else:
                                update_service_delete_file(service_delete_file, service_id, service_name)
                                ServerConnection.put_file_sftp(connection,
                                                                r'com_ericsson_do_auto_integration_files/' + service_delete_file,
                                                                SIT.get_base_folder(SIT) + service_delete_file)
                                command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={so_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d @{service_delete_file} https://{so_host_name}/service-order-mgmt/v1/serviceOrder'''
                            log.info("Curl command : %s", command)
                            Report_file.add_line("Curl command :" + command)

                            command_output = ExecuteCurlCommand.get_json_output(
                                connection, command)
                            log.info("Command output: %s", command_output)
                            Report_file.add_line("Command output: " + command_output)

                            command_out = ExecuteCurlCommand.get_sliced_command_output(
                                command_output)
                            output = ast.literal_eval(command_out)
                            delete_id = output['id']
                            log.info("service delete id: %s", delete_id)
                            Report_file.add_line("service delete id: " + delete_id)
                            thread = threading.Thread(target=work_thread, name='Thread_' + str(active),
                                                      args=(service_id, service_name, connection, so_token, delete_id))
                            thread_pool.append(thread)

        if active == 0:
            log.info("There are no active services in SO")

        if thread_pool == []:
            log.info(
                'VNF_TYPE given not found. vnf type already deleted or wrong input provided. Please check package names list from VNF-TYPE logs for more details ')

        for task in thread_pool:
            task.start()

        for task in thread_pool:
            task.join()
        print_terminate_report()
    else:
        log.info('NO Active services available in Service Orchestration gui')
        Report_file.add_line('NO Active services available in Service Orchestration gui')

    log.info('END script : SO Network service deletion ')
    Report_file.add_line('END script : SO Network service deletion ')
