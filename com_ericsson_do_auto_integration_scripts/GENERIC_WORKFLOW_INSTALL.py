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
import time
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import LCM_workflow_installation_validation
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection, get_vmvnfm_pod_cmd
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import transfer_director_file_to_vm_vnfm
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import vm_vnfm_lcm_workflow_installation_validation

log = Logger.get_logger('GENERIC_WORKFLOW_INSTALL.py')


def download_rpm(connection, command):
    """
    @param connection:
    @param command:
    """
    try:
        Report_file.add_line('wget command  ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('command output ' + command_output)

        command = 'find *.rpm | xargs ls -rt | tail -1'
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())[2:-3:]
        Report_file.add_line('rpm to be installed  ' + command_output)
        return command_output

    except Exception as e:
        log.error(f'Error downloading Generic Workflow RPM %s', str(e))
        Report_file.add_line('Error downloading Generic Workflow RPM' + str(e))
        assert False


def start_generic_workflow_install():
    """Installing Generic Workflow"""
    try:
        log.info('Starting script : Generic Workflow Install')
        Report_file.add_line('Starting script : Generic Workflow Install')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        rpm_link = sit_data._SIT__vnf_type
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        if 'TRUE' == is_vm_vnfm:
            log.info('Installing workflow on VM VNFM')
            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
            directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username
            nested_conn = get_VMVNFM_host_connection()

            log.info('Downloading RPM bundle file using the link  %s', rpm_link)
            Report_file.add_line('Downloading rpm bundle file using the link')
            command = 'wget {}'.format(rpm_link)
            rpm_name = download_rpm(nested_conn, command)

            log.info('Transferring workflow rpm to eric-vnflcm-service pod %s', rpm_name)

            source = f'/home/{directory_server_username}/{rpm_name}'
            destination = f'/tmp/{rpm_name}'

            transfer_director_file_to_vm_vnfm(nested_conn, source, destination)

            time.sleep(20)
            cmd = f"sudo -E wfmgr bundle install --package={destination}"
            command = get_vmvnfm_pod_cmd(cmd)

            vm_vnfm_lcm_workflow_installation_validation(nested_conn, command, 'Generic_workflow')
            Common_utilities.clean_up_rpm_packages(Common_utilities, nested_conn, rpm_name)

        else:
            log.info('Installing workflow on VNF LCM')
            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            lcm_conn = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            command = 'wget {}'.format(rpm_link)

            rpm_name = download_rpm(lcm_conn, command)

            rpm_path = '/home/cloud-user'
            command = 'sudo -i wfmgr bundle install --package={}/{}'.format(rpm_path, rpm_name)

            LCM_workflow_installation_validation(lcm_conn, command, 'Generic_workflow')
            Common_utilities.clean_up_rpm_packages(Common_utilities, lcm_conn, rpm_name)

        log.info('END script : Generic Workflow Install')
        Report_file.add_line('END script : Generic Workflow Install')

    except Exception as e:

        log.error('Error in Generic Workflow Install %s', str(e))
        Report_file.add_line('Error in Generic Workflow Install' + str(e))
        assert False
