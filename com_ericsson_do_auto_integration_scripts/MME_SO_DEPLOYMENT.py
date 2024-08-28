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
import ast
from packaging import version

from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import (
    update_any_flavor_file, update_transfer_flavour_file, update_image_file
)
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (
    update_runtime_env_file, update_mme_node_onboard_file, update_mme_deploy_file
)
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import check_flavor_exists
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import (
    create_flavour, image_registration
)
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import (
    get_package_status, node_ping_response, get_node_status, check_lcm_workflow_status,
    check_enm_node_sync, check_node_ecm_order_status, check_so_deploy_attribute, check_so_day1_configure_status,
    check_bulk_configuration
)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import (
    fetch_so_version, fetch_nsd_package, update_NSD_template, onboard_NSD_Template, so_files_transfer,
    onboard_enm_ecm_subsystems, onboard_so_template, create_network_service, poll_status_so
)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (
    check_image_registered, remove_host_lcm_entry, update_admin_heatstack_rights, update_lcm_oss_password,
    transfer_node_software, transfer_node_software_vm_vnfm, unpack_node_software, ssh_key_generate_on_lcm,
    onboard_node_package, deploy_node, onboard_node_hot_package
)
from com_ericsson_do_auto_integration_utilities.SO_file_update import update_mme_network_service_file
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import LCM_workflow_installation_validation
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import (
    get_VMVNFM_host_connection, get_file_name_from_vm_vnfm, get_vmvnfm_pod_cmd
)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import vm_vnfm_lcm_workflow_installation_validation

log = Logger.get_logger('MME_SO_DEPLOYMENT.py')

package_name = ''
service_template = ''
mme_zip_package = ''
mme_so_version = ''


def remove_LCM_entry_mme():
    remove_host_lcm_entry()


def admin_heatstack_rights_mme():
    update_admin_heatstack_rights()


def update_lcm_password_mme():
    update_lcm_oss_password()


def transfer_mme_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    mme_software_path = sit_data._SIT__mme_software_path
    mme_version = sit_data._SIT__mme_version
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm
    hot_file = 'sgsn-mme_hot.yaml'

    if is_vm_vnfm == 'TRUE':
        transfer_node_software_vm_vnfm('MME', mme_software_path, mme_version)
    else:
        transfer_node_software('MME', mme_software_path, mme_version, hot_file)


def unpack_mme_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    mme_version = sit_data._SIT__mme_version
    hot_file = 'sgsn-mme_hot.yaml'
    unpack_node_software('MME', mme_version, 'MME_Software_complete.tar', 'MME_Software_resources.tar', hot_file)


def mme_workflow_deployment():
    try:
        log.info('start MME workflow bundle install on LCM')
        Report_file.add_line('MME Workflow  bundle install on LCM begins...')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        mme_software_path = r'/vnflcm-ext/current/vnf_package_repo/' + sit_data._SIT__mme_version

        connection = ServerConnection.get_connection(server_ip, username, password)

        command = 'cd ' + mme_software_path + ' ;ls -ltr | grep -i .rpm'
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        rpm_name = output[-1][:-3]
        log.info('rpm name :' + rpm_name)
        log.info('command output  : ' + command_output)

        command = 'sudo -i wfmgr bundle install --package={}/{}'.format(mme_software_path, rpm_name)

        LCM_workflow_installation_validation(connection, command, 'MME')

        connection.close()
    except Exception as e:
        connection.close()
        log.info('Error EPG workflow bundle install on LCM ' + str(e))
        Report_file.add_line('Error EPG workflow bundle install on LCM ' + str(e))
        assert False


def mme_workflow_deployment_vm_vnfm():
    try:
        log.info('start MME workflow bundle install on VM-VNFM')
        Report_file.add_line('start MME workflow bundle install on VM-VNF')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vnfd_id = sit_data._SIT__mme_version
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        dir_connection = get_VMVNFM_host_connection()

        path = '/vnflcm-ext/current/vnf_package_repo/' + vnfd_id
        rpm_file = get_file_name_from_vm_vnfm(dir_connection, '.rpm', path)
        cmd = f"sudo -E wfmgr bundle install --package={path}/{rpm_file}"
        command = get_vmvnfm_pod_cmd(cmd)

        vm_vnfm_lcm_workflow_installation_validation(dir_connection, command, 'MME')

        time.sleep(2)

    except Exception as e:

        log.error('Error MME workflow bundle install on VM-VNFM ' + str(e))
        Report_file.add_line('Error MME workflow bundle install on VM-VNFM' + str(e))
        assert False
    finally:
        dir_connection.close()


def update_db_table():
    try:
        log.info('Start to update vnf-lcm db table for mme entry')
        Report_file.add_line('Start to update vnf-lcm db table for mme entry')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        old_password = 'passw0rd'

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
                interact.send(old_password + '\n')
                time.sleep(4)
                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)

                if 'UNIX password' in buff:
                    interact.send(old_password + '\n')
                    time.sleep(4)

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
                    time.sleep(5)

                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)

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

        command = 'sudo -u postgres psql'
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'postgres=' in buff:
            command = '\c vnflafdb'
            interact.send(command + '\n')
            time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'vnflafdb=' in buff:
            command = 'select * from vnflifecycledefinitionmapping;'
            interact.send(command + '\n')
            time.sleep(3)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if '(0 rows)' in buff:
            command = '''INSERT INTO vnflifecycledefinitionmapping (vnftype, vnfversion, operationtype, bundlename, definitionname, bundleversion) VALUES('SGSN-MME','1.17 (CXS101289_R78A68)', 'INSTANTIATION', 'sgsn-mme_lcm_wf_heat', 'Instantiate vSGSN-MME on OpenStack', '2.8.0');'''
            Report_file.add_line('command to insert entry in db ' + command)
            interact.send(command + '\n')
            time.sleep(3)
            command = '''INSERT INTO vnflifecycledefinitionmapping (vnftype, vnfversion, operationtype, bundlename, definitionname, bundleversion) VALUES('SGSN-MME','1.17 (CXS101289_R78A68)', 'TERMINATION', 'sgsn-mme_lcm_wf_heat', 'Terminate vSGSN-MME on OpenStack', '2.8.0');'''
            Report_file.add_line('command to insert entry in db ' + command)
            interact.send(command + '\n')
            time.sleep(3)
            command = '\q'
            interact.send(command + '\n')
            log.info('entries added successfully in db server')
        else:
            log.info(' MME entries are already exists in db server ')
            Report_file.add_line(' MME entries are already exists in db server ')

        interact.shutdown(2)
        connection.close()
        log.info('Finished to update vnf-lcm db table for mme entry')
        Report_file.add_line('Finished to update vnf-lcm db table for mme entry')
    except Exception as e:
        connection.close()
        log.info('Error to update vnf-lcm db table for mme entry')
        Report_file.add_line('Error to update vnf-lcm db table for mme entry')
        assert False


def generate_ssh_key_mme():
    ssh_key_generate_on_lcm()


def create_mme_flavors():
    log.info('start creating MME flavors')
    Report_file.add_line('start creating MME flavors')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName
    mme_flavors = sit_data._SIT__mme_flavors
    flavors_list = mme_flavors.split(',')
    for flavor_name in flavors_list:

        flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
        if flavor_exists:
            log.info('Flavor with name ' + flavor_name + ' already exists in CEE')
            Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in CEE')
        else:
            log.info('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            name = flavor_name[3:]
            if 'fsb' in name:
                update_any_flavor_file(name, 4, 8192, 160, tenant_name)
                update_transfer_flavour_file()
            elif 'ncb' in name:
                update_any_flavor_file(name, 16, 32768, 1, tenant_name)
                update_transfer_flavour_file()
            elif 'gpb' in name:
                update_any_flavor_file(name, 8, 16384, 1, tenant_name)
                update_transfer_flavour_file()
            else:
                log.warn(
                    'Flavor name does not match with requirements , please check the confluence for mme deployment ' + flavor_name)
                Report_file.add_line(
                    'Flavor name does not match with requirements , please check the confluence for mme deployment ' + flavor_name)
                assert False

            create_flavour('flavour.json', 'flavour_transfer.json', name)

    log.info('Finished creating mme flavors')
    Report_file.add_line('Finished creating mme flavors')


def create_mme_images():
    try:

        log.info('start register mme images')
        Report_file.add_line('start register mme images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vimzone_name = sit_data._SIT__vimzone_name
        mme_image_names = sit_data._SIT__mme_image_names
        mme_image_ids = sit_data._SIT__mme_image_ids
        image_names = mme_image_names.split(',')
        image_ids = mme_image_ids.split(',')
        for image_name, image_id in zip(image_names, image_ids):
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
            image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
            if image_exists:
                Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
            else:
                log.info('Going to register image with name ' + image_name)
                update_image_file('RegisterImage.json', image_name, vimzone_name, image_id)
                image_registration('RegisterImage.json')

        log.info('Finished register mme images')
        Report_file.add_line('Finished register mme images')
        connection.close()
    except Exception as e:
        connection.close()
        log.error('Error register mme images ' + str(e))
        Report_file.add_line('Error register mme images ' + str(e))
        assert False


def mme_so_files_transfer():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    mme_software_path = sit_data._SIT__mme_software_path
    node_package_name = sit_data._SIT__mme_package_name

    global mme_so_version
    mme_so_version = fetch_so_version('MME')
    so_files_transfer(mme_software_path, 'MME', node_package_name, mme_so_version)


def upload_ipam():
    try:
        log.info(' start uploading IPAM Network')
        Report_file.add_line(' start uploading IPAM Network begins...')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        mme_software_path = sit_data._SIT__mme_software_path

        token_user = 'so-user'
        token_password = 'Ericsson123!'
        token_tenant = 'master'
        # Fetching IPAM SO Version separately in PRE-REQUSITE JOB 
        ipam_mme_so_version = fetch_so_version('MME')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_host_name = sit_data._SIT__so_host_name
        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)

        ServerConnection.get_file_sftp(connection, mme_software_path + '/networkupload.csv',
                                       r'com_ericsson_do_auto_integration_files/networkupload.csv')

        if ipam_mme_so_version <= version.parse('2.0.0-117'):

            log.info('fetching IPAM networkupload.csv from ECM')
            file_name = 'networkupload.csv'

        else:

            log.info('fetching IPAM networkupload_new.csv from ECM')
            file_name = 'networkupload_new.csv'

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        if ipam_mme_so_version <= version.parse('2.0.0-117'):

            curl = '''curl --insecure 'https://{}/ip-manager/eso/v1.0/ipam/' -H "Accept: application/json" -H 'Cookie: JSESSIONID="{}"{}'''.format(
                so_host_name, so_token, "'")

        else:

            curl = '''curl --insecure 'https://{}/ipam/v2/subnet-pools' -H "Accept: application/json" -H 'Cookie: JSESSIONID="{}"{}'''.format(
                so_host_name, so_token, "'")

        command = curl
        log.info(command)
        Report_file.add_line('command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        log.info(command_out)

        output = ast.literal_eval(command_out)
        total_items = output['total']
        log.info(total_items)

        if total_items == 8:

            log.info('IPAM already exist')
            Report_file.add_line('IPAM already exist')

        else:

            log.info('Uploading IPAM on SO')
            Report_file.add_line('Uploading IPAM on SO')
            if ipam_mme_so_version <= version.parse('2.0.0-117'):

                curl = '''curl -i --insecure -X POST -F file=@"{}" -H 'Cookie: JSESSIONID="{}"' -H 'Content-Type: multipart/form-data' 'https://{}/ip-manager/eso/v1.0/ipam/upload{}'''.format(
                    file_name, so_token, so_host_name, "'")

            else:

                curl = '''curl -i --insecure -X POST -F file=@"{}" -H 'Cookie: JSESSIONID="{}"' -H 'Content-Type: multipart/form-data' 'https://{}/ipam/v2/subnet-pools/upload{}'''.format(
                    file_name, so_token, so_host_name, "'")

            command = curl
            log.info(command)
            Report_file.add_line('command : ' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('closing connection')
        connection.close()

    except Exception as e:
        connection.close()
        log.error('Error in IPAM Network Upload ' + str(e))
        Report_file.add_line('Error in IPAM Network upload ' + str(e))
        assert False


def update_mme_onboard_file():
    log.info('Connecting with VNF-LCM server')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

    mme_software_path = sit_data._SIT__mme_software_path

    is_vm_vnfm = sit_data._SIT__is_vm_vnfm
    node_version = sit_data._SIT__mme_version

    path = mme_software_path + '/' + node_version

    global mme_zip_package

    mme_zip_package = node_version + '.zip'

    log.info('Getting VNFD_Wrapper_SGSN-MME.json and {} from server to get onboard params'.format(mme_zip_package))
    Report_file.add_line('Getting VNFD_Wrapper_SGSN-MME.json and {} from server to get onboard params'.format(
        mme_zip_package))
    global package_name
    if is_vm_vnfm == 'TRUE':
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'VNFM_MME')

        ServerConnection.get_file_sftp(connection,
                                       path + '/Resources/VnfdWrapperFiles/VNFD_Wrapper_SGSN-MME.json',
                                       r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SGSN-MME.json')
        ServerConnection.get_file_sftp(connection, path + '/' + mme_zip_package,
                                       r'com_ericsson_do_auto_integration_files/' + mme_zip_package)


    else:
        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
        package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'TEST_MME')
        try:

            ServerConnection.get_file_sftp(connection,
                                           r'/vnflcm-ext/current/vnf_package_repo/' + node_version + '/Resources/VnfdWrapperFiles/VNFD_Wrapper_SGSN-MME.json',
                                           r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SGSN-MME.json')
            ServerConnection.get_file_sftp(connection,
                                           r'/vnflcm-ext/current/vnf_package_repo/' + node_version + '/' + mme_zip_package,
                                           r'com_ericsson_do_auto_integration_files/' + mme_zip_package)

        except Exception as e:
            log.error('Error while getting the VNFD_Wrapper_SGSN-MME.json or {} from server Error : {}'.format(
                mme_zip_package, str(e)))

    connection.close()

    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SGSN-MME.json')

    sit_data._SIT__mme_package_name = package_name
    log.info('MME ONBOARD PACKAGE NAME ' + package_name)
    Report_file.add_line('MME ONBOARD PACKAGE NAME ' + package_name)

    onboard_file_name = 'onboard_mme.json'
    upload_file = mme_zip_package
    update_mme_node_onboard_file(r'com_ericsson_do_auto_integration_files/' + onboard_file_name, file_data,
                                 package_name)

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + onboard_file_name,
                                   SIT.get_base_folder(SIT) + onboard_file_name)
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + upload_file,
                                   SIT.get_base_folder(SIT) + upload_file)
    connection.close()


def onboard_mme_package():
    onboard_node_package('onboard_mme.json', mme_zip_package, package_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnfPackage_id = sit_data._SIT__mme_packageId
    update_runtime_env_file('MME_PACKAGE_ID', vnfPackage_id)


def verify_mme_package():
    log.info('start verifying the onboarded mme package')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

    core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    vnf_packageId = sit_data._SIT__mme_packageId
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

    provisioningStatus, operationalState = get_package_status(connection, token, core_vm_hostname, vnf_packageId)

    if 'ACTIVE' in provisioningStatus and 'ENABLED' in operationalState:

        Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
        Report_file.add_line('operationalState is : ' + operationalState)
        log.info('Verification of package uploaded is success')
        Report_file.add_line('Verification of package Upload is success')
        log.info('Finished onboarding package for ' + package_name)
        Report_file.add_line('Finished onboarding package for ' + package_name)
        connection.close()
    else:

        log.error(
            'Verification of package uploaded failed. Please check the status of provisioning and operationalState  ')
        log.error('provisioningStatus : ' + provisioningStatus + ' operationalState : ' + operationalState)
        Report_file.add_line(
            'Verification of package uploaded failed. Please check the status of provisioning and operationalState')
        connection.close()
        assert False


def onboard_ipam_package():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    mme_software_path = sit_data._SIT__mme_software_path
    ipam_package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'IPAM_PACKAGE')
    upload_file = 'ipam_network_HOT.yml'
    onboard_node_hot_package(ipam_package_name, upload_file, mme_software_path)


def fetch_mme_nsd_package():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    mme_software_path = sit_data._SIT__mme_software_path
    global nsd_package
    global service_template

    if mme_so_version <= version.parse('1.2.2083'):
        nsd_package = 'mme1_so_nsd.csar'
        service_template = 'ST_MME.yml'

    elif mme_so_version >= version.parse('2.0.0-70'):
        nsd_package = 'mme1_so_nsd_new.csar'
        service_template = 'ST_MME_CATALOG_new.yml'

    else:
        nsd_package = 'mme1_so_nsd.csar'
        service_template = 'ST_MME_CATALOG.yml'

    fetch_nsd_package(mme_software_path, nsd_package, service_template, mme_so_version)


def update_mme_nsd_template():
    if mme_so_version <= version.parse('2.0.0-69'):

        unzipped_nsd_package = 'mme1_so_nsd'
        zipped_nsd_package = 'mme1_so_nsd.zip'
        update_NSD_template(nsd_package, unzipped_nsd_package, zipped_nsd_package, 'MME', mme_so_version)

    else:

        log.info('No need to update NS1.yaml in this version of SO ' + str(mme_so_version))


def onboard_mme_subsytems():
    onboard_enm_ecm_subsystems('MME')


def onboard_mme_nsd_template():
    onboard_NSD_Template(nsd_package, service_template, 'MME', mme_so_version)


def onboard_mme_service_template():
    file_name = service_template
    onboard_so_template(file_name, 'MME', mme_so_version)


def create_mme_network_service():
    if mme_so_version >= version.parse('2.11.0-118'):

        file_name = 'create_mme_NetworkService_serviceOrder.json'
        update_mme_network_service_file(file_name, mme_so_version)
        payload = Json_file_handler.get_json_data(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        create_network_service(payload, mme_so_version)
    else:
        file_name = 'create_mme_NetworkService_new.json'

        update_mme_network_service_file(file_name, mme_so_version)
        create_network_service(file_name, mme_so_version)


def check_mme_so_deploy_attribute():
    check_so_deploy_attribute(1800)


def check_mme_so_day1_configure_status():
    check_so_day1_configure_status()


def check_mme_lcm_workflow_status():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__mme_package_name
    node_defination_name = 'Instantiate vSGSN-MME on OpenStack'
    check_lcm_workflow_status(node_package_name, node_defination_name)


def check_mme_enm_sync_status():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__mme_package_name
    check_enm_node_sync(node_package_name)


def check_mme_ip_ping_status():
    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SGSN-MME.json')
    ip_address = file_data['instantiateVnfOpConfig']['vnfIpAddress']
    node_ping_response(ip_address)


def check_mme_ecm_order():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__mme_package_name
    package_id = sit_data._SIT__mme_packageId
    check_node_ecm_order_status(node_package_name, package_id)


def verify_mme_service_status():
    poll_status_so()


def update_mme_oss_model_id():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__mme_package_name


def check_mme_bulk_configuration():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__mme_package_name
    command = 'cmedit get MeContext= ' + node_package_name + ',ManagedElement=' + node_package_name + ',MmeFunction=1'
    check_bulk_configuration('MME', 'es:userLabel', command, mme_so_version)


def update_deploy_file_mme_ecm():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

    node_name = sit_data._SIT__mme_package_name
    file_name = 'deploy_mme.json'

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SGSN-MME.json')
    update_mme_deploy_file(r'com_ericsson_do_auto_integration_files/' + file_name, file_data, node_name)
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                   SIT.get_base_folder(SIT) + file_name)
    log.info('Going to start deployment of node ' + node_name)
    connection.close()


def deploy_mme_package_ecm():
    deploy_node('deploy_mme.json', 'MME')


def verify_mme_deployment_ecm():
    timeout = 60
    try:

        log.info('waiting ' + str(timeout) + ' seconds to verification of node')
        time.sleep(timeout)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        node_id = sit_data._SIT__vapp_Id
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_SGSN-MME.json')
        # ip_address = file_data['instantiateVnfOpConfig']['vnfIpAddress']
        # ping_response = get_ping_response(connection, ip_address)

        provisioningStatus, operationalState = get_node_status(connection, token, core_vm_hostname, node_id)

        if provisioningStatus == 'ACTIVE' and operationalState == 'INSTANTIATED':

            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)
            log.info('Verification of package deployment is success')
            Report_file.add_line('Verification of package deployment is successful')
            connection.close()

        else:
            log.info(
                'Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response ')
            Report_file.add_line(
                'Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response')
            connection.close()
            assert False


    except Exception as e:
        connection.close()
        log.error('Error verifying node deployment ' + str(e))
        Report_file.add_line('Error verifying node deployment ' + str(e))
        assert False
