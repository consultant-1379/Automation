# pylint: disable = C0301, C0103, C0116, W0212, W0703, C0209, R0915, R0914

import ast
import time

from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_injest_file
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.SO_NODE_DELETION import change_db_passwd_when_permission_denied
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (
    vm_vnfm_lcm_workflow_installation_validation,
    LCM_workflow_installation_validation
)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DELETION import get_vapp_list_from_eocm
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import (
    get_VMVNFM_host_connection,
    Server_details,
    get_master_vnflcm_db_pod, get_vmvnfm_pod_cmd
)

log = Logger.get_logger('ECM_NODE_REDISCOVERY.py')

stack_idd = ''


def fetch_vdc_name_id_EOCM(vapp_name, node_name):
    try:
        log.info('start fetching vdc id and vdc name for %s', vapp_name)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP

        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)

        vapp_list = get_vapp_list_from_eocm(connection, token, core_vm_hostname, vapp_name)

        for vapp_data in vapp_list:
            name = vapp_data['name']
            if vapp_name == name:
                vdc_name = vapp_data['vdc']['name']
                vdc_id = vapp_data['vdc']['id']
                log.info('Found the VDC name %s and vdc_id %s', vdc_name, vdc_id)
                log.info('Finished fetching vdc id and vdc name for %s', vapp_name)
                return vdc_name, vdc_id

        return '', ''
    except Exception as error:
        log.error('Error fetching vdc id and vdc name for %s', str(error))
        Report_file.add_line('Error fetching vdc id and vdc name for ' + str(error))
    finally:
        connection.close()


def discovery_workflow_deployment(node_name):
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        if is_vm_vnfm == 'TRUE':

            log.info('Start to deploy discovery vm vnflm workflow for %s', node_name)
            log.info('start discovery workflow bundle install on VM VNFM')
            Report_file.add_line('Discovery Workflow  bundle install on VM VNFM begins...')

            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            discovery_link = ecm_host_data._Ecm_core__discovery_bundle_link
            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
            connection = get_VMVNFM_host_connection()

            log.info(
                'Downloading discovery workflow bundle file using the link provided in the DIT: %s',
                discovery_link
            )
            Report_file.add_line('Downloading discovery workflow bundle file using the link provided in DIT')

            cmd = f"wget {discovery_link}"

            command = get_vmvnfm_pod_cmd(cmd)

            stdin, stdout, stderr = connection.exec_command(command)
            time.sleep(70)
            log.info('Executing: %s', command)

            command_output = str(stdout.read())
            log.info('command output %s', command_output)

            cmd = "find ERICvnfadmin*.rpm | xargs ls -rt | tail -1"
            command = get_vmvnfm_pod_cmd(cmd)
            stdin, stdout, stderr = connection.exec_command(command)

            command_output = str(stdout.read())[2:-3:]
            log.info(command_output)

            if 'No such file or directory' in command_output:

                log.error('Error to find discovery workflow bundle on VM VNFM ')
                assert False

            else:

                workflowname = command_output
                path = "/home/eric-vnflcm-service"
                log.info('discover workflow rpm name : %s', workflowname)
                log.info('Discovery Workflow rpm file downloaded is: %s', command_output)
                Report_file.add_line('Discovery Workflow rpm  bundlefile downloaded succesfully.')
                cmd = f"sudo -E wfmgr bundle install --package={path}/{workflowname}"
                command = get_vmvnfm_pod_cmd(cmd)

                vm_vnfm_lcm_workflow_installation_validation(connection, command, node_name)
                Common_utilities.clean_up_rpm_packages(Common_utilities, connection, workflowname)

        else:

            log.info('Start to deploy discovery vnflcm workflow for %s', node_name)
            log.info('start discovery workflow bundle install on LCM')
            Report_file.add_line('Discovery Workflow  bundle install on LCM begins...')

            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

            server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP

            username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
            password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
            discovery_link = ecm_host_data._Ecm_core__discovery_bundle_link

            connection = ServerConnection.get_connection(server_ip, username, password)

            log.info(
                'Downloading discovery workflow bundle file using the link provided in the DIT: %s',
                discovery_link
            )
            Report_file.add_line('Downloading discovery workflow bundle file using the link provided in DIT')

            command = 'wget {}'.format(discovery_link)
            stdin, stdout, stderr = connection.exec_command(command)
            time.sleep(70)
            log.info('Executing: %s', command)

            command_output = str(stdout.read())
            log.info('command output: %s', command_output)

            command = 'find ERICvnfadmin*.rpm | xargs ls -rt | tail -1'
            stdin, stdout, stderr = connection.exec_command(command)

            command_output = str(stdout.read())[2:-3:]
            log.info(command_output)

            workflowname = command_output
            log.info('discover workflow rpm name : %s', workflowname)
            log.info('Discovery Workflow rpm file downloaded is: %s', command_output)
            Report_file.add_line('Discovery Workflow rpm  bundlefile downloaded succesfully.')

            command = 'sudo -i wfmgr bundle install --package=/home/cloud-user/{}'.format(workflowname)

            LCM_workflow_installation_validation(connection, command, node_name)
            Common_utilities.clean_up_rpm_packages(Common_utilities, connection, workflowname)

    except Exception as error:
        log.error('Error to install discovery workflow bundle install on LCM %s', str(error))
        Report_file.add_line('Error to install discovery workflow bundle install on LCM ' + str(error))
        assert False
    finally:
        connection.close()


def delete_vapp_entry_cmdb(vappname, vdcname):
    try:
        log.info('start deleting vapp entry from cmdb %s', vappname)
        Report_file.add_line('start deleting vapp entry from cmdb... ' + vappname)

        core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        username = core_vm_data._Ecm_PI__CORE_VM_USERNAME
        password = core_vm_data._Ecm_PI__CORE_VM_PASSWORD
        deployment_type = core_vm_data._Ecm_PI__deployment_type

        if deployment_type == 'HA':
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_IP

        cmdb_password = Common_utilities.fetch_cmdb_password(Common_utilities)

        connection = ServerConnection.get_connection(core_vm_ip, username, password)

        cmdbdelete = '''./cmdbDelete.sh -username cmdb -password {} -tenant ECM -objectType vapp -objectNames "{}|{}" -mode commit -logLevel DEBUG'''.format(
            cmdb_password, vdcname, vappname
        )

        interact = connection.invoke_shell()
        command = 'su ecm_admin'
        interact.send(command + '\n')
        time.sleep(2)

        command = 'cd /app/ecm/tools/cmdb/cmdb-util/util'
        interact.send(command + '\n')
        time.sleep(2)

        command = cmdbdelete
        interact.send(command + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if 'want to continue (y/n)' in buff:
            command = 'y'
            interact.send(command + '\n')
            time.sleep(30)
            resp = interact.recv(99999)
            buff = str(resp)
            log.info(buff)

        Report_file.add_line('vapp deletion from cmdb output: ' + buff)
        interact.shutdown(2)
        if 'Exit Code: 0' in buff:
            log.info('vapp deleted from cmdb successfully')
            Report_file.add_line('vapp deletion from cmdb successfully')

        else:
            log.error(
                'vapp deletion from cmdb failed. Check the logs under /app/ecm/tools/cmdb/cmdb-util/logs'
            )
            Report_file.add_line(
                'vapp deletion from cmdb failed. Check the logs under /app/ecm/tools/cmdb/cmdb-util/logs'
            )
            log.error('Script terminated : vapp deletion from cmdb failed')
            Report_file.add_line('Script terminated : vapp deletion from cmdb failed')
            assert False

        log.info('vapp deletion from cmdb ends')
        Report_file.add_line('vapp deletion from cmdb ends...')

    except Exception as error:

        log.error('Error to delete vapp from cmdb %s', str(error))
        Report_file.add_line('Error to delete vapp from cmdb')
        assert False
    finally:
        connection.close()


def delete_vapp_vnflcmdb(vapp_name):
    try:
        log.info('start deleting vapp from vnflcmdb %s', vapp_name)
        Report_file.add_line('start deleting vapp from vnflcmdb ' + vapp_name)

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if is_vm_vnfm == 'TRUE':

            vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)

            connection = get_VMVNFM_host_connection()

            interact = connection.invoke_shell()

            master_pod = get_master_vnflcm_db_pod(connection)

            command = f'kubectl exec -it {master_pod} -c eric-vnflcm-db -n {vm_vnfm_namespace} -- /bin/bash'
            interact.send(command + '\n')
            time.sleep(3)

            command = 'psql -U postgres -d vnflafdb'
            interact.send(command + '\n')
            time.sleep(3)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

        else:

            server_ip = Ecm_core.get_vnf_lcm_servicedb_ip(Ecm_core)
            username = Ecm_core.get_vnf_lcm_servicedb_username(Ecm_core)
            password = Ecm_core.get_vnf_lcm_servicedb_password(Ecm_core)

            log.info(
                'Logging to VNFLCM with the new password and Proceeding to start delete vapp from vnflcmdb'
            )

            connection = ServerConnection.get_connection(server_ip, username, password)
            interact = connection.invoke_shell()
            time.sleep(2)
            command = 'sudo -i'
            interact.send(command + '\n')
            time.sleep(2)
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
                    log.info('Permission denied , password has been changed . Going to set it again')
                    change_db_passwd_when_permission_denied(interact, password)

            command = 'sudo -u postgres psql -d vnflafdb'
            interact.send(command + '\n')
            time.sleep(3)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

        command = f"DELETE FROM vnfscaleinfo WHERE VNFID=(select vnfid from vnfs where vnfname='{vapp_name}');" \
                  f"DELETE FROM instantiatedvnf WHERE VNFID=(select vnfid from vnfs where vnfname='{vapp_name}');" \
                  f"DELETE FROM vnflifecycleattributes WHERE vnflifecycleoperationid IN " \
                  f"(SELECT vnflifecycleoperationid FROM vnflifecycleoperation " \
                  f"WHERE VNFID=(select vnfid from vnfs where vnfname='{vapp_name}'));" \
                  f"DELETE FROM vnflifecycleoperation WHERE " \
                  f"VNFID=(select vnfid from vnfs where vnfname='{vapp_name}');" \
                  f"DELETE FROM VNFS WHERE VNFID=(select vnfid from vnfs where vnfname='{vapp_name}');"

        log.info("vnflaf db command :: %s ", command)

        interact.send(command + '\n')
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if 'DELETE 1' in buff:
            log.info('vapp is deleted from vnflaf db: %s', buff)
            Report_file.add_line('vapp is deleted from vnflaf db:' + buff)
        else:
            log.info('Error deleting vapp from vnflaf db : %s', buff)
            Report_file.add_line('Error deleting vapp from vnflaf db :' + buff)
            assert False

        interact.shutdown(2)

        log.info('Finished deleting record from vnflafdb tables')
        Report_file.add_line('Finished deleting record from vnflafdb tables')
    except Exception as error:
        log.error('Error deleting vapp from vnflaf db: %s', str(error))
        Report_file.add_line('Error deleting vapp from vnflaf db ' + str(error))
        assert False
    finally:
        connection.close()


def list_discovery(vapp_name):
    try:
        log.info('Qwery API to check list of Discovery: %s', vapp_name)
        Report_file.add_line('Qwery API to check list of Discovery:...' + vapp_name)

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vimzone_name = sit_data._SIT__vimzone_name
        project_id = sit_data._SIT__project_system_id

        curl = '''curl  --insecure --location --request GET 'https://{}/ecm_service/stacks?$filter=vimZone=%27{}%27%20%27and%27%20projectId=%27{}%27' --header 'tenantid: ECM' --header 'Content-Type: application/json' --header 'Authorization: Basic ZWNtYWRtaW46Q2xvdWRBZG1pbjEyMw=={}'''.format(
            core_vm_hostname, vimzone_name, project_id, "'"
        )
        command = curl
        Report_file.add_line('Curl command to list the discovery:' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        Report_file.add_line('Discovery list : ' + command_output)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)

        stack_list = output['data']['queryStacks']['stacks']

        requestStatus = output['status']['reqStatus']
        global stack_idd
        stack_idd = ''
        if 'SUCCESS' in requestStatus:

            for item in stack_list:
                stackname = item['stackName']
                if vapp_name == stackname:
                    stack_idd = item['stackId']
                    log.info('Stack id for the node is: %s', stack_idd)
                    break

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command while executing discovery curl command %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command while executing discovery curl command ')
            assert False

        if stack_idd == '':
            log.info('The requested Stack is not found for the discovered stack list %s', stack_idd)
            assert False

        log.info('Executing discovery curl command ends')
        Report_file.add_line('executing discovery curl command ends...')

    except Exception as error:
        log.error('Error Executing discovery curl %s', str(error))
        Report_file.add_line('Error executing discovery curl ' + str(error))
        assert False
    finally:
        connection.close()


def discover_vapp(STACK_NAME, VNFM_ID, VNF_NAME, VDC_ID, VNFPACKGE_ID, VIMZONE_NAME):
    try:
        log.info('start discover vapp %s', STACK_NAME)
        Report_file.add_line('start discover vapp... ' + STACK_NAME)
        core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        core_vm_hostname = core_vm_data._Ecm_PI__core_vm_hostname

        core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_IP

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('creating the domain using the token for authentication')

        log.info('STACK_NAME: %s', STACK_NAME)
        log.info('VNFM_ID: %s', VNFM_ID)
        log.info('VDC_ID: %s', VDC_ID)
        log.info('VNFPACKGE_ID: %s', VNFPACKGE_ID)

        file_name = 'injest.json'

        update_injest_file(
            file_name, VDC_ID, VNFM_ID, stack_idd, STACK_NAME, VNFPACKGE_ID, VNF_NAME, VIMZONE_NAME
        )

        ServerConnection.put_file_sftp(
            connection, r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name
        )

        curl = '''curl --insecure -X POST 'https://{}/ecm_service/ingestStacks' --header 'tenantid: ECM' --header 'Content-Type: application/json' --data @{} --header 'Authorization: Basic ZWNtYWRtaW46Q2xvdWRBZG1pbjEyMw=={}'''.format(
            core_vm_hostname, file_name, "'"
        )

        command = curl
        Report_file.add_line('Discovery vApp curl command: ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Discovery vApp curl output ' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            order_id = output['data']['order']['id']
            order_status, order_output = Common_utilities.orderReqStatus(
                Common_utilities, connection, token, core_vm_hostname, order_id, 10
            )

            if order_status:
                log.info('Order Status is completed %s', order_id)
                Report_file.add_line('Order Status is completed ' + order_id)
                log.info('Discovery vApp completed successfully ')
                Report_file.add_line('Discovery vApp order completed successfully')
            else:
                log.info('Order Status for discover vapp is failed with message mentioned above %s', order_id)
                Report_file.add_line(
                    'Order Status for discover vapp is failed with message mentioned above ' + order_id
                )
                assert False

        elif 'ERROR' in requestStatus:
            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for discover vapp %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for discover vapp')
            assert False

    except Exception as error:
        log.error('Error Executing discovery curl %s', str(error))
        Report_file.add_line('Error executing discovery curl ' + str(error))
        assert False
    finally:
        connection.close()


def delete_vapp_from_cmdb_ecm(node_name, file_name):
    """
    delete vapp name from cmdb using eocm curl command
    """
    log.info('Start to delete vapp %s from cmdb', node_name)
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        ecm_gui_username = Ecm_core.get_ecm_gui_username(Ecm_core)
        ecm_gui_password = Ecm_core.get_ecm_gui_password(Ecm_core)
        tenant_name = SIT.get_tenant_name(SIT)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecm_gui_username, ecm_gui_password)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        command = f'curl -i --insecure -X POST --header "Authorization:Basic {auth_basic}"' \
                  f' --header "TenantId:{tenant_name}"' \
                  f' https://{core_vm_hostname}:443/ecm_service/cmdb/dbutils/cmdbdelete' \
                  f' --header "Content-Type: application/json" --data @{file_name} '

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '200 OK' in command_output:
            # virtual application count will be 1 in output in successful case
            if '"Virtual Application":1' in command_output:
                log.info('Finished deleting vapp %s from cmdb', node_name)
            else:
                log.error("Error deleting vapp %s from cmdb, "
                          "please check logs and file data %s", node_name, file_name)
                assert False
        else:
            log.error("Error in deleting Vapp from cmdb , please check logs")
            assert False

    except Exception as e:
        log.error('Error while deleting Vapp from cmdb %s', str(e))
        assert False

    finally:
        if connection:
            connection.close()
