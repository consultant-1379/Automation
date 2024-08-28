# pylint: disable=C0302,C0103,C0301,C0412,E0602,W0621,C0411,R0915,E0602,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612
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
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import ast
import time
from xml.dom import minidom
from tabulate import tabulate
from packaging import version

# Note : Do NOT import SO_NODE_DELETION and SO_NODE_DEPLOYMENT files here to avoid circular import

log = Logger.get_logger('VERIFY_NODE_DEPLOYMENT.py')

table_data = []


def print_report_table():
    log.info(tabulate(table_data, headers=["VERIFICATION STEP", "RESULT"], tablefmt='grid', showindex="always"))
    Report_file.add_line(tabulate(table_data, headers=["VERIFICATION STEP", "RESULT"], tablefmt='grid',
                                  showindex="always"))


def change_db_passwd_when_permission_denied_verify(interact, password):
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


def verify_result_in_vnflaf_db(node_name, param_name, db_query, result, is_vm_vnfm):
    try:
        log.info('Start verifing configurable parameter * {} * for Vnf_type * {} * in vnflaf DB '.format(param_name,
                                                                                                         node_name))
        Report_file.add_line('Start verifing configurable parameter * {} * for Vnf_type * {} * in vnflaf DB'.format(
            param_name, node_name))

        if 'TRUE' == is_vm_vnfm:

            connection = get_VMVNFM_host_connection()
            stdin, stdout, stderr = connection.exec_command(db_query)

            buff = str(stdout.read())
            Report_file.add_line('Query result - ' + buff)


        else:

            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)

            connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

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
                interact.send(lcm_password + '\n')
                time.sleep(4)
                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                if 'Permission denied' in buff:
                    log.info('Permission denied , password has been changed . Going to set it again')
                    change_db_passwd_when_permission_denied_verify(interact, lcm_password)

            command = '''sudo -u postgres psql -d vnflafdb '''
            interact.send(command + '\n')
            time.sleep(4)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'vnflafdb=' in buff:
                command = db_query
                interact.send(command + '\n')
                time.sleep(4)

            resp = interact.recv(9999)

            buff = resp.decode(encoding='UTF-8')

            log.info(buff)
            Report_file.add_line('Query result - ' + buff)

            interact.shutdown(2)

        output = buff.replace('\n', '')
        output = output.replace('\r', '')

        Report_file.add_line('Output : ' + output)

        if result in output:
            log.info('Successfully verified configurable parameter * {} * for Vnf_type * {} * in vnflaf DB'.format(
                param_name, node_name))
            Report_file.add_line(
                'Successfully verified configurable parameter * {} * for Vnf_type * {} * in vnflaf DB'.format(
                    param_name, node_name))
        else:
            log.error('Verification failed .Somthing went wrong in vnflaf DB , check the output ' + buff)
            Report_file.add_line('Verification failed .Somthing went wrong in vnflaf DB , check the output ' + buff)
            assert False

    except Exception as e:

        log.error('Error verifing configurable parameter' + str(e))
        Report_file.add_line('Error verifing configurable parameter ' + str(e))
        assert False
    finally:

        connection.close()


def get_package_status(connection, token, core_vm_ip, package_id):
    log.info('curl command of verification of uploading the package')

    command = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/vnfpackages/{}'''.format(
        token, core_vm_ip, package_id + "'")

    Report_file.add_line('Curl command for verifying OnBoarding the package ' + command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)
    requestStatus = output['status']['reqStatus']

    provisioningStatus = ''
    operationalState = ''
    if 'SUCCESS' in requestStatus:

        provisioningStatus = output['data']['vnfPackage']['provisioningStatus']
        operationalState = output['data']['vnfPackage']['operationalState']
        log.info('provisioningStatus is : ' + provisioningStatus)
        log.info('operationalState is : ' + operationalState)

    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for verification of OnBoard package ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for verification of OnBoard package')

    return provisioningStatus, operationalState


def get_package_upload_status(connection, token, core_vm_ip, vnf_instance_id, time_out, wait_time):
    try:
        while (time_out > 0):
            provisioningStatus, operationalState = get_package_status(connection, token, core_vm_ip, vnf_instance_id)

            if 'ACTIVE' in provisioningStatus and 'ENABLED' in operationalState:
                Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
                Report_file.add_line('operationalState is : ' + operationalState)
                log.info("Successfully Uploaded the package  ")
                Report_file.add_line("Successfully Uploaded the package ")
                return 'UPLOADED'
            if 'ERROR' in provisioningStatus and 'DISABLED' in operationalState:
                Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
                Report_file.add_line('operationalState is : ' + operationalState)
                log.info(" ERROR Uploaded the package  ")
                Report_file.add_line("ERROR Uploaded the package ")
                return 'UPLOAD FAILED'
            else:
                log.info('provisioningStatus is : ' + provisioningStatus)
                log.info('operationalState is : ' + operationalState)
                log.info('Waiting for 90 sec to check package upload status again')
                time_out = time_out - wait_time
                time.sleep(wait_time)
        if time_out == 0:
            log.info("Waiting time has been exceeded to check package upload status ")
            Report_file.add_line("Waiting time has been exceeded to check package upload status")
            assert False
    except Exception as e:
        log.info(e)


def get_ping_response(connection, ip_address):
    log.info('Start checking ping response for ' + ip_address)
    cmd = 'ping -w 3 ' + ip_address
    log.info('Pinging ip address' + ip_address)
    Report_file.add_line('Pinging ip address' + ip_address)

    stdin, stdout, stderr = connection.exec_command(cmd)
    cmd_output = str(stdout.read())
    cmd_error = str(stderr.read())
    response = False
    data_loss = ' 100% packet loss'
    if cmd_output.find(data_loss) == -1:

        log.info('Ping Successful ' + cmd_output)
        Report_file.add_line('Ping Successful ' + cmd_output)
        return True

    else:
        log.info('No Response from Ping ' + cmd_output)
        Report_file.add_line('No Response from Ping ' + cmd_output)
        return False


def node_ping_response(ip_address):
    try:
        log.info('Start checking ping response for ' + ip_address)
        Report_file.add_line('Pinging ip address' + ip_address)
        log.info('waiting 60 seconds for node to come up fully')
        time.sleep(60)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        cmd = 'ping -w 3 ' + ip_address
        stdin, stdout, stderr = connection.exec_command(cmd)
        cmd_output = str(stdout.read())
        cmd_error = str(stderr.read())
        global table_data
        data_loss = ' 100% packet loss'
        if cmd_output.find(data_loss) == -1:

            log.info('Ping Successful ' + cmd_output)
            Report_file.add_line('Ping Successful ' + cmd_output)
            data = ['NODE PING RESPONSE', 'PASS']
            table_data.append(data)


        else:
            log.info('No Response from Ping ' + cmd_output)
            Report_file.add_line('No Response from Ping ' + cmd_output)
            data = ['NODE PING RESPONSE', 'FAIL']
            table_data.append(data)
            print_report_table()
            assert False, 'No Response from Ping ' + ip_address


    except Exception as e:
        connection.close()
        log.info('Error checking ping response for ' + ip_address)
        Report_file.add_line('Error checking ping response for ' + ip_address)
        assert False


def get_node_status(connection, token, core_vm_ip, node_id):
    log.info('curl command of verification of deployment')
    command = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/vapps/{}'''.format(
        token, core_vm_ip, node_id + "'")

    command_output = ExecuteCurlCommand.get_json_output(connection, command)

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus']
    provisioningStatus = ''
    operationalState = ''
    if 'SUCCESS' in requestStatus:
        try:

            provisioningStatus = output['data']['vapp']['provisioningStatus']
            operationalState = output['data']['vapp']['operationalStatus']
            log.info('provisioningStatus is : ' + provisioningStatus)
            log.info('operationalState is : ' + operationalState)
        except Exception as e:
            log.info('provisioningStatus is : ' + provisioningStatus)
            log.info('No operational state is present for vapp id ' + node_id)


    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for status of deployed node ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for status of deployed node ')
    return provisioningStatus, operationalState


def check_lcm_workflow_status(node_package_name, node_defination_name):
    try:
        log.info(
            'Start to check lcm_workflow_status for ' + node_package_name + ' , node defination name is ' + node_defination_name)
        Report_file.add_line(
            'Start to check lcm_workflow_status for ' + node_package_name + ' , node defination name is ' + node_defination_name)

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if 'TRUE' == is_vm_vnfm:
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
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
            username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
            password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

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
                    change_db_passwd_when_permission_denied_verify(interact, password)

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
        global table_data
        if '(0 rows)' in buff:
            log.error('No record found for requested node package name')
            log.error('workflow failed in between , please check the workflow logs for details')
            data = ['LCM WORKFLOW STATUS', 'NOT FOUND']
            table_data.append(data)
            assert False
        else:
            index = buff.index(node_package_name + '_')
            new_string = buff[index:]
            data_list = new_string.split('|')
            log.info(len(data_list))
            if len(data_list) == 4:

                if 'prg__p100' in data_list[2] and 'prg__p100' in data_list[3]:
                    log.info(
                        'workflow is successfully completed with lastpnodeid {} and endnodeid {}'.format(data_list[2],
                                                                                                         data_list[3]))
                    Report_file.add_line(
                        'workflow is successfully completed with lastpnodeid {} and endnodeid {}'.format(
                            data_list[2], data_list[3]))
                    data = ['LCM WORKFLOW STATUS', 'PASS']
                    table_data.append(data)

                elif 'EndEvent_instantiateNode_end' in data_list[3]:
                    log.info(
                        'workflow is successfully completed with lastpnodeid {} and endnodeid {}'.format(data_list[2],
                                                                                                         data_list[3]))
                    Report_file.add_line(
                        'workflow is successfully completed with lastpnodeid {} and endnodeid {}'.format(
                            data_list[2], data_list[3]))
                    data = ['LCM WORKFLOW STATUS', 'PASS']
                    table_data.append(data)
                elif 'EndEvent_1__failure' in data_list[3]:
                    log.error('some failure at very end of node deployment lastpnodeid is ' + data_list[
                        2] + 'and endnodeid is ' + data_list[3])
                    data = ['LCM WORKFLOW STATUS', 'FAIL']
                    table_data.append(data)
                    assert False

                else:
                    log.error('some failure at very end of node deployment lastpnodeid is ' + data_list[
                        2] + 'and endnodeid is ' + data_list[3])
                    data = ['LCM WORKFLOW STATUS', 'FAIL']
                    table_data.append(data)
                    assert False
            else:
                log.error('error in quering the database for workflow check ')
                log.error('output is : ' + new_string)
                assert False
        interact.shutdown(2)
        connection.close()
        log.info('Finished to check lcm_workflow_statusfor ' + node_package_name)
        Report_file.add_line('Finished to check lcm_workflow_statusfor ' + node_package_name)
    except Exception as e:
        connection.close()
        log.info('Error to check lcm_workflow_statusfor ' + node_package_name)
        Report_file.add_line('Error to check lcm_workflow_statusfor ' + node_package_name)
        assert False


def update_command_file(command):
    try:
        command_line = '''command = {}{}{}\n'''.format("'", command, "'")
        command_file = open(r'com_ericsson_do_auto_integration_files/enm_command_runner.txt', 'r')
        data_list = command_file.readlines()
        command_file.close()

        command_file = open(r'com_ericsson_do_auto_integration_files/enm_command_runner.txt', 'w+')
        for line in data_list:
            if 'command =' in line:
                command_file.write(command_line)
            else:
                command_file.write(line)
        log.info('finished updating the enm_command_runner.txt')
    except Exception as e:

        log.info('Error updating the enm_command_runner.txt')
        Report_file.add_line('Error updating the enm_command_runner.txt')
        assert False


def enm_tosca_node_cleanup():
    """
    This method is to clean up tosca node in ENM.
    """
    log.info("Starting cleanup of tosca node in network viewer")
    try:
        node_name = SIT.get_tosca_epg_vapp(SIT)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        enm_hostname, enm_username, enm_password = Server_details.enm_host_server_details(Server_details)
        enm_token = Common_utilities.generate_enm_token(Common_utilities, connection, enm_hostname, enm_username,
                                                        enm_password)

        enm_node_cleanup(node_name, enm_hostname, connection, enm_token)

    except IOError as error:
        log.error('ENM tosca node cleanup failed: %s', str(error))
        assert False

    except Exception as error:
        log.error('ENM tosca node cleanup failed: %s', str(error))
        assert False


def enm_etsi_tosca_node_cleanup():
    """
    This method is to clean up etsi tosca node in ENM.
    """
    log.info("Starting cleanup of etsi tosca node in network viewer")
    try:
        node_name = SIT.get_etsi_tosca_epg_vapp(SIT)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        enm_hostname, enm_username, enm_password = Server_details.enm_host_server_details(Server_details)
        enm_token = Common_utilities.generate_enm_token(Common_utilities, connection, enm_hostname, enm_username,
                                                        enm_password)

        enm_node_cleanup(node_name, enm_hostname, connection, enm_token)

    except IOError as error:
        log.error('ENM etsi tosca node cleanup failed: %s', str(error))
        assert False

    except Exception as error:
        log.error('ENM etsi tosca node cleanup failed: %s', str(error))
        assert False


def enm_node_cleanup(enm_node_name, enm_hostname, connection, enm_token):
    """
    To clean up / delete nodes in ENM network viewer.
    """
    url = f"https://{enm_hostname}/network-visualization/v1/network-elements/{enm_node_name}"
    log.info(url)
    try:
        if enm_node_name:
            log.info("Deleting node %s from ENM ", enm_node_name)
            command = ('''curl --insecure "{}" \
                                -X DELETE -H "Accept: */*" \
                                -H "Content-Type: application/json" -H "Cookie: iPlanetDirectoryPro={}"'''
                       .format(url, enm_token))
            log.info("Curl command: %s", command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

            if command_out == '':
                log.info("Successfully deleted node: %s", enm_node_name)

            elif command_out == 'ERR_CODE_NE_NOT_PRES_IN_DPS':
                log.info("Unsuccessfully deleted node: %s", enm_node_name)
                log.info("Node is not present or has been deleted already")

            else:
                log.info("Error while executing the curl command: %s", command_out)
                assert False
        else:
            log.info("Node is not present")

    except IOError as error:
        log.error('ENM delete node cleanup failed: %s', str(error))
        assert False

    except Exception as error:
        log.error('ENM delete node cleanup failed: %s', str(error))
        assert False


def check_enm_node_sync(node_package_name):
    try:
        log.info('Start to check node sync status in ENM ' + node_package_name)
        Report_file.add_line('Start to check node sync status in ENM ' + node_package_name)
        enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
        server_ip = enm_data._Vnfm__enm_ipaddress
        user_name = enm_data._Vnfm__authUserName
        password = enm_data._Vnfm__authPassword
        connection = ServerConnection.get_connection(server_ip, user_name, password)

        command = 'cmedit get ' + node_package_name + ' cmfunction.syncstatus'
        update_command_file(command)

        ServerConnection.put_file_sftp(connection,
                                       r'com_ericsson_do_auto_integration_files/enm_command_runner.txt',
                                       '/home/shared/administrator/enm_command_runner.py')

        command = 'python /home/shared/administrator/enm_command_runner.py'
        timeout = 300
        log.info('Time out for this process is 5 mins')
        break_flag = False
        while timeout != 0:

            if break_flag:
                break

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line(command_output)
            output = command_output[2:-1:1]

            list_out = output.split('\\n')
            Report_file.add_line(list_out)
            global table_data
            for item in list_out:
                if 'syncStatus' in item:
                    data = item.split(' : ')
                    if 'SYNCHRONIZED' == data[1]:
                        log.info(node_package_name + '  node successfully synced to enm')
                        Report_file.add_line(node_package_name + '  node successfully synced to enm')
                        data = ['ENM NODE SYNC STATUS', 'PASS']
                        table_data.append(data)
                        print_report_table()
                        break_flag = True
                        connection.close()
                        break
                    elif 'UNSYNCHRONIZED' == data[1]:
                        log.info(node_package_name + '  node sync status is UNSYNCHRONIZED')
                        Report_file.add_line(node_package_name + '   node sync status is UNSYNCHRONIZED')
                        log.info('Waiting for 20 sec to check the ENM sync status again')
                        timeout = timeout - 20
                        time.sleep(20)
                        break
                    else:
                        log.info(node_package_name + '  node sync status is PENDING ')
                        Report_file.add_line(node_package_name + '  node sync status is PENDING ')
                        log.info('Waiting for 20 sec to check the ENM sync status again')
                        timeout = timeout - 20
                        time.sleep(20)
                        break

                elif 'error' in item:
                    log.error('error to check node sync status in ENM')
                    Report_file.add_line('error to check node sync status in ENM ' + item)
                    assert False
        if timeout == 0:
            log.error('Automation script timed out ,Node is not synced in ENM ')
            Report_file.add_line('Automation script timed out ,Node is not synced in ENM ')
            data = ['ENM NODE SYNC STATUS', 'FAIL']
            table_data.append(data)
            print_report_table()
            connection.close()
            assert False, node_package_name + ' is UNSYNCRONIZED in ENM , please check ENM logs'

    except Exception as e:
        connection.close()
        log.info('Error to check node sync status in ENM ' + node_package_name)
        Report_file.add_line('Error to check node sync status in ENM ' + node_package_name)
        assert False


def check_node_ecm_order_status(node_package_name, package_id):
    try:
        log.info('Start to check ECM order status for ' + node_package_name)
        Report_file.add_line('Start to check ECM order status for ' + node_package_name)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)

        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        core_vm = core_vm_hostname if is_cloudnative else core_vm_ip
        command = '''curl --insecure -X GET --header 'Accept: application/json' --header 'AuthToken:{}' 'https://{}/ecm_service/orders?$filter=searchTag%3DVNFPKG%7C{}%7C{}{}'''.format(
            token, core_vm, node_package_name, package_id, "'")

        Report_file.add_line('Curl command for getting ECM order number and status ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']
        global table_data
        if 'SUCCESS' in requestStatus:
            if 'data' in output.keys():
                order_id = output['data']['orders'][0]['id']
                log.info('order id for ' + node_package_name + ' in ECM ' + order_id)
                Report_file.add_line('order id for ' + node_package_name + ' in ECM ' + order_id)
                order_status = output['data']['orders'][0]['orderReqStatus']
                log.info('ECM order status is ' + order_status)
                if 'COM' in order_status:

                    log.info('Order status for order id ' + order_id + ' is completed')
                    Report_file.add_line('Order status for order id ' + order_id + ' is completed')
                    data = ['ECM ORDER STATUS', 'PASS']
                    table_data.append(data)
                    print_report_table()

                elif 'ERR' in order_status:
                    log.error('Order Status is failed ' + order_id)
                    Report_file.add_line('Order Status is failed ' + order_id)
                    data = ['ECM ORDER STATUS', 'FAIL']
                    table_data.append(data)
                    print_report_table()
                    assert False, 'Order Status is failed ' + order_id + ' ,please check ECM logs'
                else:
                    log.info('Order Status is still in progress ' + order_id)
                    Report_file.add_line('Order Status is still in progress ' + order_id)
                    data = ['ECM ORDER STATUS', 'FAIL']
                    table_data.append(data)
                    print_report_table()
                    assert False, 'Order Status is still in progress ' + order_id + ', please check order status in ECM'


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command check ECM order status ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command check ECM order status')
            connection.close()
            assert False

    except Exception as e:
        connection.close()
        log.error('Error to check ECM order status for ' + node_package_name)
        Report_file.add_line('Error to check ECM order status for ' + node_package_name)
        assert False


def check_so_attribute_status(connection, command):
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    global table_data
    output = ast.literal_eval(command_out)
    try:
        state = output[0]['state']
        log.info('SO version is new checking for state attribute')
        so_version = 'new_version'

    except:
        log.info('SO version is old checking for complete and success attribute')
        so_version = 'old_version'

    return so_version, output


def check_so_deploy_attribute(timeout):
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_host_name = sit_data._SIT__so_host_name
        service_id = sit_data._SIT__network_service_id
        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password

        log.info('Start checking in SO for workflow deployment status for service id ' + service_id)
        Report_file.add_line('Start checking in SO for workflow deployment status for service id ' + service_id)

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)

        command = '''curl --insecure -X GET -H 'Cookie: JSESSIONID="{}"' 'https://{}/orchestrationcockpit/eso/v1.0/services/{}/executionPlan{}'''.format(
            so_token, so_host_name, service_id, "'")
        Report_file.add_line('command :' + command)
        log.info('timeout for this process is ' + str(timeout))
        data = []
        global table_data
        while timeout != 0:

            so_version, output = check_so_attribute_status(connection, command)

            if 'Service Unavailable' in output:

                log.info('waiting 60 seconds to check again the state')
                timeout = timeout - 60
                time.sleep(60)
            elif 'Access Denied' in output:
                log.warning('Access Denied in the output , generating token again ')
                so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                              token_password, token_tenant)

                command = '''curl --insecure -X GET -H 'Cookie: JSESSIONID="{}"' 'https://{}/orchestrationcockpit/eso/v1.0/services/{}/executionPlan{}'''.format(
                    so_token, so_host_name, service_id, "'")

                Report_file.add_line('Updated command :' + command)
                log.info('waiting 60 seconds to retry ')
                timeout = timeout - 60
                time.sleep(60)

            elif 'old_version' == so_version:
                complete_status = output['steps'][0]['complete']
                if complete_status == True:

                    success_status = output['steps'][0]['success']

                    if success_status == True:
                        log.info('From SO , workflow deployment status for service id ' + service_id + ' is success')
                        Report_file.add_line(
                            'From SO , workflow deployment status for service id ' + service_id + ' is success')
                        data = ['SO DEPLOY ATTRIBUTE', 'PASS']
                        table_data.append(data)
                        break
                    else:
                        log.error('From SO , workflow deployment status for service id ' + service_id + ' is failed')
                        Report_file.add_line(
                            'From SO , workflow deployment status for service id ' + service_id + ' is failed')
                        data = ['SO DEPLOY ATTRIBUTE', 'FAIL']
                        table_data.append(data)
                        assert False, 'From SO , workflow deployment status for service id ' + service_id + ' is failed, please check SO logs'
                else:
                    log.info('From SO , workflow deployment status for service id ' + service_id + ' is inProgress')
                    Report_file.add_line(
                        'From SO , workflow deployment status for service id ' + service_id + ' is inProgress')
                    log.info('waiting 60 seconds to check again the status')
                    timeout = timeout - 60
                    time.sleep(60)

            elif 'new_version' == so_version:
                state = output[0]['state']
                if 'Completed' == state:

                    log.info('From SO , workflow deployment state for service id ' + service_id + ' is completed')
                    Report_file.add_line(
                        'From SO , workflow deployment state for service id ' + service_id + ' is completed')
                    data = ['SO DEPLOY ATTRIBUTE', 'PASS']
                    table_data.append(data)
                    break
                elif 'InProgress' == state or 'New' == state:
                    log.info('From SO , workflow deployment state for service id ' + service_id + ' is ' + state)
                    Report_file.add_line(
                        'From SO , workflow deployment state for service id ' + service_id + ' is ' + state)
                    log.info('waiting 60 seconds to check again the state')
                    timeout = timeout - 60
                    time.sleep(60)

                else:
                    log.error('From SO , workflow deployment state for service id ' + service_id + ' is ' + state)
                    Report_file.add_line(
                        'From SO , workflow deployment state for service id ' + service_id + ' is ' + state)
                    data = ['SO DEPLOY ATTRIBUTE', 'FAIL']
                    table_data.append(data)
                    assert False, 'From SO , workflow deployment state for service id ' + service_id + ' is failed, please check SO logs'

        if timeout == 0:
            log.info('Automation script timed out ,Please check SO logs something went wrong')
            Report_file.add_line('Automation script timed out ,Please check SO logs something went wrong')
            data = ['SO DEPLOY ATTRIBUTE', 'FAIL']
            table_data.append(data)
            assert False

    except Exception as e:
        connection.close()
        log.info('Error checking in SO for workflow deployment status for service id ' + service_id)
        Report_file.add_line('Error checking in SO for workflow deployment status for service id ' + service_id)
        assert False


def check_so_day1_configure_status():
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        service_id = sit_data._SIT__network_service_id
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_host_name = sit_data._SIT__so_host_name
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password

        log.info('Start checking in SO for day1 configure status for service id ' + service_id)
        Report_file.add_line('Start checking in SO for day1 configure status for service id ' + service_id)

        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)
        command = '''curl --insecure -X GET -H 'Cookie: JSESSIONID="{}"' 'https://{}/orchestrationcockpit/eso/v1.0/services/{}/executionPlan{}'''.format(
            so_token, so_host_name, service_id, "'")
        Report_file.add_line('command :' + command)

        log.info('waiting 20 seconds just node to sync in ENM')

        time.sleep(20)

        global table_data

        timeout = 1800

        log.info('timeout for this process is 30 mins (1800 seconds)')

        while timeout != 0:

            so_version, output = check_so_attribute_status(connection, command)

            if 'Service Unavailable' in output:

                log.info('waiting 30 seconds to check again the state')
                timeout = timeout - 30
                time.sleep(30)
            elif 'Access Denied' in output:
                log.warning('Access Denied in the output , generating token again ')
                so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                              token_password, token_tenant)
                command = '''curl --insecure -X GET -H 'Cookie: JSESSIONID="{}"' 'https://{}/orchestrationcockpit/eso/v1.0/services/{}/executionPlan{}'''.format(
                    so_token, so_host_name, service_id, "'")

                Report_file.add_line('Updated command :' + command)
                log.info('waiting 30 seconds to retry ')
                timeout = timeout - 30
                time.sleep(30)

            elif 'old_version' == so_version:

                complete_status = output['steps'][1]['complete']
                if complete_status == True:

                    success_status = output['steps'][1]['success']

                    if success_status == True:
                        log.info('From SO , day1 configure status for service id ' + service_id + ' is success')
                        Report_file.add_line(
                            'From SO , day1 configure status for service id ' + service_id + ' is success')
                        data = ['SO DAY1 CONFIGURE ATTRIBUTE', 'PASS']
                        table_data.append(data)
                        break

                    else:
                        log.error('From SO , day1 configure success status for service id ' + service_id + ' is failed')
                        Report_file.add_line(
                            'From SO , day1 configure success status for service id ' + service_id + ' is failed')
                        data = ['SO DAY1 CONFIGURE ATTRIBUTE', 'FAIL']
                        table_data.append(data)
                        assert False, 'From SO , day1 configure success status for service id ' + service_id + ' is failed , please check SO logs'
                else:
                    log.error('From SO , day1 configure complete status for service id ' + service_id + ' is failed')
                    Report_file.add_line(
                        'From SO , day1 configure complete status for service id ' + service_id + ' is failed')
                    data = ['SO DAY1 CONFIGURE ATTRIBUTE', 'FAIL']
                    table_data.append(data)
                    assert False, 'From SO , day1 configure complete status for service id ' + service_id + ' is failed , please check SO logs'


            elif 'new_version' == so_version:

                state = output[1]['state']

                if 'Completed' == state:
                    log.info('From SO , day1 configure state for service id ' + service_id + ' is completed')
                    Report_file.add_line(
                        'From SO , day1 configure state for service id ' + service_id + ' is completed')
                    data = ['SO DAY1 CONFIGURE ATTRIBUTE', 'PASS']
                    table_data.append(data)
                    break

                elif 'InProgress' == state:
                    log.info('From SO , day1 configure state for service id ' + service_id + ' is ' + state)
                    Report_file.add_line('From SO , day1 configure state for service id ' + service_id + ' is ' + state)
                    log.info('waiting 30 seconds to check again the state')
                    timeout = timeout - 30
                    time.sleep(30)

                else:
                    log.error('From SO , day1 configure state for service id ' + service_id + ' is ' + state)
                    Report_file.add_line('From SO , day1 configure state for service id ' + service_id + ' is ' + state)
                    data = ['SO DAY1 CONFIGURE ATTRIBUTE', 'FAIL']
                    table_data.append(data)
                    assert False, 'From SO , day1 configure state for service id ' + service_id + ' is failed , please check SO logs'

        if timeout == 0:
            log.info('Automation script timed out ,Please check SO logs something went wrong')
            Report_file.add_line('Automation script timed out ,Please check SO logs something went wrong')
            data = ['SO DAY1 CONFIGURE ATTRIBUTE', 'FAIL']
            table_data.append(data)
            assert False



    except Exception as e:
        connection.close()
        log.info('Error checking in SO for day1 configure status for service id ' + service_id)
        Report_file.add_line('Error checking in SO for day1 configure status for service id ' + service_id)
        assert False


def check_state_network_service(connection, command):
    # All the errors are handled in execute_curl_get_json_output method
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    output = ast.literal_eval(command_out)

    return output


def tosca_scale_service_state_check():
    """
    Poll Network Service on the basis of Service ID
    """
    try:
        log.info('start polling network Service state on the basis of service id for scale')
        Report_file.add_line('polling network Service state on the basis of service id begins for scale...')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_host_name = sit_data._SIT__so_host_name
        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'
        service_id = sit_data._SIT__network_service_id
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password

        log.info(f'Network service id : {service_id}')

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)
        log.info('Polling SO network service using the token for authentication and Service Id for scale')

        Report_file.add_line('Polling SO network service using the token for authentication and Service Id for scale')
        log.info('time out for this process is 60 mins')
        timeout = 3600

        command = f'''curl --insecure -H 'Cookie: JSESSIONID="{so_token}"' 'https://{so_host_name}/orchestration/v1/services/{service_id}{"'"}'''

        log.info(command)
        Report_file.add_line('command :' + command)
        global table_data
        while timeout != 0:

            state_output = check_state_network_service(connection, command)

            state = state_output['state']

            if 'Service Unavailable' in state:
                log.info('waiting 30 seconds to check again the state')
                time.sleep(30)
            elif 'Service Temporarily Unavailable' in state:
                log.info('Service Temporarily Unavailable, waiting 30 seconds to check again the state')
                time.sleep(30)
            elif 'Active' in state:
                log.info('Network service is created successfully with state ' + state)
                Report_file.add_line('Network service is created successfully with state ' + state)
                connection.close()
                data = ['SO NETWORK SERVICE STATUS', 'PASS']
                table_data.append(data)
                break
            elif 'InProgress' in state or 'New' in state:
                log.info('Network service creation  ongoing with state ' + state)
                Report_file.add_line('Network service  creation  ongoing with state ' + state)
                log.info('waiting 60 seconds to check again the state')
                timeout = timeout - 60
                time.sleep(60)
            else:
                log.error('Network Service state ' + state)
                log.error('Error in Network Service Creation , check the SO logs')
                Report_file.add_line('Error in Network Service Creation , check the SO logs')
                connection.close()
                data = ['SO NETWORK SERVICE STATUS', 'FAIL']
                table_data.append(data)
                assert False, 'Network Service state ' + state
                break
        if timeout == 0:
            log.info('Automation script timed out after 60 minutes, Network Service state : ' + state)
            Report_file.add_line('Automation script timed out after 60 minutes, Network Service state : ' + state)
            assert False
    except Exception as e:
        log.error("Error while polling scale service state Error Message for scale: %s", str(e))
        Report_file.add_line("Error while polling Scale service state Error Message : " + str(e))
        assert False
    finally:
        connection.close()


def check_so_network_service_state(poll_so_version):
    try:

        log.info('start polling network Service state on the basis of service id ')
        Report_file.add_line('polling network Service state on the basis of service id begins...')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_host_name = sit_data._SIT__so_host_name
        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'
        service_id = sit_data._SIT__network_service_id
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password

        log.info(f'Network service id : {service_id}')

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)

        log.info('Polling SO network service using the token for authentication and Service Id')

        Report_file.add_line('Polling SO network service using the token for authentication and Service Id ')
        log.info('time out for this process is 60 mins')
        timeout = 3600

        if poll_so_version >= version.parse('2.11.0-118'):
            command = f'''curl --insecure -H 'Cookie: JSESSIONID="{so_token}"' 'https://{so_host_name}/service-order-mgmt/v1/serviceOrder/{service_id}{"'"}'''

        else:

            command = f'''curl --insecure -H 'Cookie: JSESSIONID="{so_token}"' 'https://{so_host_name}/orchestration/v1/services/{service_id}{"'"}'''

        global table_data
        counter = 0
        while timeout != 0:

            state_output = check_state_network_service(connection, command)

            service_order_state = state_output['state']

            if poll_so_version >= version.parse('2.11.0-118'):

                if 'assessing' in service_order_state:
                    counter += 1
                    if counter > 2:
                        log.error(f'Network service order status is Assessing for service id {service_id}')
                        Report_file.add_line(
                            f'Network service order status is Assessing for service id {service_id}')
                        assert False
                    else:
                        log.info(f'Network service order status is Assessing for service id {service_id}')
                        Report_file.add_line(
                            f'Network service order status is Assessing for service id {service_id}')
                        log.info('waiting 30 seconds to check again the state')
                        timeout = timeout - 30
                        time.sleep(30)

                elif 'completed' in service_order_state:
                    log.info(f'Network service order status is completed for service id {service_id}')
                    Report_file.add_line(f'Network service order status is completed for service id {service_id}')

                    log.info('Checking Network service state and service order item state')

                    service_order_item_state = state_output['serviceOrderItem'][0]['state']
                    service_state = state_output['serviceOrderItem'][0]['service']['state']

                    log.info(
                        f'Network service order item is {service_order_item_state} and service state is {service_state} ')
                    Report_file.add_line(
                        f'Network service order item is {service_order_item_state} and service state is {service_state} ')

                    if service_order_item_state == "completed" and service_state == "active":

                        log.info(f'Verification successful for service id {service_id}')

                        data = ['SO NETWORK SERVICE STATUS', 'PASS']
                        table_data.append(data)
                        break
                    else:
                        log.error("Verification failed , check the above status for network service ")
                        data = ['SO NETWORK SERVICE STATUS', 'FAIL']
                        table_data.append(data)
                        assert False

                elif 'inProgress' in service_order_state or 'new' in service_order_state:
                    log.info(
                        f'Network service creation for service id {service_id} ongoing with order status {service_order_state}')
                    Report_file.add_line(
                        f'Network service creation for service id {service_id} ongoing with order status {service_order_state}')
                    log.info('waiting 60 seconds to check again the state')
                    timeout = timeout - 60
                    time.sleep(60)
                else:
                    log.error('Network Service order status is %s ', service_order_state)
                    log.error('Error in Network Service Creation , check the SO logs')
                    Report_file.add_line('Error in Network Service Creation , check the SO logs')
                    data = ['SO NETWORK SERVICE STATUS', 'FAIL']
                    table_data.append(data)
                    assert False

            else:
                if 'Active' in service_order_state:
                    log.info('Network service is created successfully with state ' + service_order_state)
                    Report_file.add_line('Network service is created successfully with state ' + service_order_state)
                    data = ['SO NETWORK SERVICE STATUS', 'PASS']
                    table_data.append(data)
                    break
                elif 'InProgress' in service_order_state or 'New' in service_order_state:
                    log.info('Network service creation  ongoing with state ' + service_order_state)
                    Report_file.add_line('Network service  creation  ongoing with state ' + service_order_state)
                    log.info('waiting 60 seconds to check again the state')
                    timeout = timeout - 60
                    time.sleep(60)
                else:
                    log.error('Network Service state ' + service_order_state)
                    log.error('Error in Network Service Creation , check the SO logs')
                    Report_file.add_line('Error in Network Service Creation , check the SO logs')
                    data = ['SO NETWORK SERVICE STATUS', 'FAIL']
                    table_data.append(data)
                    assert False

        if timeout == 0:
            log.warning('Automation script timed out after 60 minutes, Network Service state : ' + service_order_state)
            Report_file.add_line(
                'Automation script timed out after 60 minutes, Network Service state : ' + service_order_state)
            assert False

    except Exception as e:
        log.error("Error while polling service state Error Message : %s", str(e))
        Report_file.add_line("Error while polling service state Error Message : " + str(e))
        assert False

    finally:
        if connection:
            connection.close()


def check_bulk_configuration(node_name, attribute_name, command, node_so_version):
    log.info('Start to check bulk cm import for ' + node_name)
    Report_file.add_line('Start to check bulk cm import for' + node_name)
    enm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
    server_ip = enm_data._Vnfm__enm_ipaddress
    user_name = enm_data._Vnfm__authUserName
    password = enm_data._Vnfm__authPassword
    connection = ServerConnection.get_connection(server_ip, user_name, password)

    if node_so_version >= version.parse('2.0.0-70'):

        day1_file_name = 'day1Config' + node_name + '_new.xml'

    else:
        day1_file_name = 'day1Config' + node_name + '.xml'

    mydoc = minidom.parse(r'com_ericsson_do_auto_integration_files/' + day1_file_name)
    item = mydoc.getElementsByTagName(attribute_name)
    attribute_value = item[0].firstChild._data

    Report_file.add_line('attribute value ' + attribute_value)

    update_command_file(command)

    ServerConnection.put_file_sftp(connection,
                                   r'com_ericsson_do_auto_integration_files/enm_command_runner.txt',
                                   '/home/shared/administrator/enm_command_runner.py')
    command = 'python /home/shared/administrator/enm_command_runner.py'

    stdin, stdout, stderr = connection.exec_command(command)
    output_list = []
    for line in stdout:
        output_list.append(line)

    Report_file.add_line('output items ' + str(output_list))

    global table_data

    if 'location : ' + attribute_value + '\n' in output_list and node_name == 'EPG':
        log.info('Bulk Cm import for ' + node_name + ' is successful')
        Report_file.add_line('Bulk Cm import for ' + node_name + ' is successful')
        data = ['BULK IMPORT STATUS', 'PASS']
        table_data.append(data)
        print_report_table()
        connection.close()

    elif 'userLabel : ' + attribute_value + '\n' in output_list and node_name == 'MME':
        log.info('Bulk Cm import for ' + node_name + ' is successful')
        Report_file.add_line('Bulk Cm import for ' + node_name + ' is successful')
        data = ['BULK IMPORT STATUS', 'PASS']
        table_data.append(data)
        print_report_table()
        connection.close()

    else:
        log.info('Bulk Cm import for ' + node_name + ' is Failed')
        Report_file.add_line('Bulk Cm import for ' + node_name + ' is Failed')
        data = ['BULK IMPORT STATUS', 'FAIL']
        table_data.append(data)
        print_report_table()
        connection.close()
        assert False, 'Bulk import status is failed for ' + node_name + ' ENM output from query is ' + str(
            output_list)
