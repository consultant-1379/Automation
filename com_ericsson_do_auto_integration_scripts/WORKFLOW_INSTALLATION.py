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
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import *
from tabulate import tabulate

log = Logger.get_logger('WORKFLOW_INSTALLATION.py')

rpm_dir_path = "/var/tmp/installrpm"
lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(Server_details)
vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)

report_table_data = []


def print_wf_install_report():
    try:
        log.info(tabulate(report_table_data, headers=["RPM_NAME", "RESULT", "PRE_INSTALL", "POST_INSTALL", "MESSAGE"],
                          tablefmt='grid', showindex="always"))
        Report_file.add_line(tabulate(report_table_data,
                                      headers=["RPM_NAME", "RESULT", "PRE_INSTALL", "POST_INSTALL",
                                               "MESSAGE"],
                                      tablefmt='grid', showindex="always"))

        for data in report_table_data:
            if 'FAILED' in data:
                log.error('Failure in installation of minimum one rpm , please check the above table for more details')
                Report_file.add_line(
                    'Failure in installation of minimum one rpm , please check the above table for more details')
                assert False

    except Exception as e:
        log.error('Error printing table' + str(e))
        Report_file.add_line('Error printing table' + str(e))
        assert False


def get_workflow_list_from_blade_to_install(connection, rpm_type):
    """Fetching the workflow list"""
    log.info('Getting the workflow list')
    Report_file.add_line('Getting the workflow list')
    ftp = connection.open_sftp()
    rpms_list = ftp.listdir(rpm_dir_path)
    rpm_jenkins_input_list = rpm_type.split(",")
    final_rpm_list = []
    for rpm_jenkins_input in rpm_jenkins_input_list:

        if "ALL" == rpm_jenkins_input.strip():
            return rpms_list

        for rpm in rpms_list:
            if rpm_jenkins_input.strip() in rpm:
                final_rpm_list.append(rpm)

    return final_rpm_list


def transfer_workflows_to_vnflcm_vmvnfm_server(connection, is_vm_vnfm):
    """ transfer the workflow on LCM or VMVNFM"""

    if 'TRUE' == is_vm_vnfm:
        log.info('Transferring the workflow on vm vnfm')
        Report_file.add_line('Transferring the workflow on vm vnfm')

        if vm_vnfm_namespace == 'codeploy':

            # ServerConnection.put_file_sftp(connection, 'id_rsa_tf.pem', '/root/id_rsa_tf.pem')
            file_path = 'id_rsa_tf.pem'

        else:
            # ServerConnection.put_file_sftp(connection, 'eccd-2-3.pem', '/root/eccd-2-3.pem')
            file_path = 'eccd-2-3.pem'

        destination_filepath = '/home/' + vm_vnfm_director_username + "/"

        source_filepath = r'/var/tmp/installrpm'

        # Transferring file from blade server to vm vnfm director server
        ServerConnection.transfer_files_with_an_encrypted_pem_file(connection, file_path,
                                                                   source_filepath, vm_vnfm_director_username,
                                                                   vm_vnfm_director_ip, destination_filepath)

        source = '/home/' + vm_vnfm_director_username + "/installrpm"
        destination = '/tmp'
        dir_connection = get_VMVNFM_host_connection()
        transfer_director_file_to_vm_vnfm(dir_connection, source, destination)
        dir_connection.close()
        log.info('Transferring of workflow on vm vnfm is completed')
        Report_file.add_line('Transferring of workflow on vm vnfm is completed')
    else:
        log.info('Transferring the workflow on LCM')
        Report_file.add_line('Transferring the workflow on LCM')
        source_path = '/var/tmp/installrpm'
        destination_path = '/home/' + lcm_username + "/"
        log.info('transferring installrpm folder to LCM')
        filepath = '/' + ecm_username + '/'
        ServerConnection.transfer_folder_between_remote_servers(connection, lcm_server_ip,
                                                                lcm_username, lcm_password, source_path,
                                                                destination_path, filepath, "put")

        log.info('Transferring of workflow on LCM is completed')
        Report_file.add_line('Transferring of workflow on LCM is completed')


def create_workflow_install_cmd(install_wf_list, is_vm_vnfm):
    log.info('Preparing the command ')
    Report_file.add_line('Preparing the command')
    if 'TRUE' == is_vm_vnfm:
        server_path = "/installrpm/"
    else:
        server_path = '/home/' + lcm_username + "/installrpm/"
    command = "wfmgr bundle install --package"

    for wf in install_wf_list:
        command = command + " " + server_path + wf

    return command


def execute_validate_wf_command(connection, command):
    """Executing and validating the command"""
    log.info('executing the command')
    Report_file.add_line('executing the command')

    success_list = ['success', 'success', 'success', 'package installation successful']
    skipped_list = ['skipped', 'skipped', 'skipped', 'Higher or same version of package is already installed']

    stdin, stdout, stderr = connection.exec_command(command)

    command_output = str(stdout.read())
    command_output = command_output.split("post_install")[1]
    table_data = command_output.split('\\n')
    log.info('command output  %s', str(table_data))
    Report_file.add_line('command output ' + str(table_data))

    for row in range(2, len(table_data) - 2):

        column_data = table_data[row].split('|')

        workflow_rpm_name = column_data[1].strip()
        result_list = [column_data[2].strip(), column_data[3].strip(), column_data[4].strip(),
                       column_data[5].strip()]

        log.info('result_list %s', str(result_list))
        Report_file.add_line('result_list' + str(result_list))

        if result_list == skipped_list or result_list == success_list:
            result = "SUCCESSFUL"
            Report_file.add_line(f'RPM installation Successfully/Skipped for {workflow_rpm_name}')
        else:
            result = "FAILED"
            Report_file.add_line(f'wf installation failed for {workflow_rpm_name}')

        report_data = [workflow_rpm_name, result, column_data[2].strip(), column_data[3].strip(),
                       column_data[4].strip(),
                       column_data[5].strip()]

        log.info('appending the table with data')
        report_table_data.append(report_data)

    print_wf_install_report()


def execute_workflow_command_validate(wf_install_cmd, is_vm_vnfm):
    """ Command for workflow install"""
    if "TRUE" == is_vm_vnfm:
        connection = get_VMVNFM_host_connection()
        cmd = f"sudo -E {wf_install_cmd}"
        command = get_vmvnfm_pod_cmd(cmd)
        log.info('command for VM VNFM -%s', command)
        Report_file.add_line('command for VM VNFM ' + command)

    else:
        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username,
                                                     lcm_password)
        command = f"sudo -i {wf_install_cmd}"
        log.info('command for LCM -%s', command)
        Report_file.add_line('command for LCM ' + command)

    execute_validate_wf_command(connection, command)


def workflow_rpm_install():
    """Workflow Installation"""
    try:

        log.info('Start Installing workflow rpm ')
        Report_file.add_line('Start Installing workflow rpm')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        rpm_type = sit_data._SIT__vnf_type
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm
        log.info('connecting with ECM Blade')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        install_wf_list = get_workflow_list_from_blade_to_install(connection, rpm_type)
        Report_file.add_line('Workflow list to be installed : ' + str(install_wf_list))

        transfer_workflows_to_vnflcm_vmvnfm_server(connection, is_vm_vnfm)

        wf_intall_cmd = create_workflow_install_cmd(install_wf_list, is_vm_vnfm)

        log.info('Closing ECM connection')
        connection.close()
        execute_workflow_command_validate(wf_intall_cmd, is_vm_vnfm)

    except Exception as e:

        log.info('Error Installing workflow rpm ' + str(e))
        Report_file.add_line('Error Installing workflow rpm' + str(e))
        assert False
