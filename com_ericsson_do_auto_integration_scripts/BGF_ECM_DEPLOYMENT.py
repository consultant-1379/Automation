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
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_bgf_onboard_file,
                                                                         update_bgf_deploy_file)
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import (update_any_flavor_file,
                                                                          update_transfer_flavour_file,
                                                                          update_image_file
                                                                          )
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import check_flavor_exists
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import (create_flavour,
                                                                            image_registration)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (remove_host_lcm_entry,
                                                                          update_admin_heatstack_rights,
                                                                          update_lcm_oss_password,
                                                                          get_vnfd_id_ims_nodes,
                                                                          transfer_node_software_vnflcm,
                                                                          unpack_node_software,
                                                                          ssh_key_generate_on_lcm,
                                                                          check_image_registered,
                                                                          onboard_node_package,
                                                                          deploy_node
                                                                          )
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import (get_package_status,
                                                                             get_node_status)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import so_files_transfer
import time
import random

log = Logger.get_logger('BGF_ECM_DEPLOYMENT.py')

package_name = ''


def remove_LCM_entry():
    remove_host_lcm_entry()


def admin_heatstack_rights():
    update_admin_heatstack_rights()


def update_lcm_password():
    update_lcm_oss_password()


# method to get folder name that is named upon bfg software folder
def get_vnfd_id_bgf_nodes():
    get_vnfd_id_ims_nodes('BGF', 'deployBGF')


# new changes for IMS nodes
def transfer_bgf_software():
    transfer_node_software_vnflcm('BGF', 'deployBGF')


# Not in use after auto download from Node ARM Repo
def unpack_bgf_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    bgf_version = sit_data._SIT__bgf_version
    hot_file = 'vbgf.yaml'
    unpack_node_software('BGF', bgf_version, 'BGF_Software_complete.tar', 'BGF_Software_resources.tar',
                         hot_file)


def bgf_workflow_deployment():
    connection = None
    try:
        log.info('start BGF workflow bundle install on LCM')
        Report_file.add_line('BGF Workflow  bundle install on LCM begins...')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        bgf_software_path = r'/var/tmp/' + sit_data._SIT__bgf_version

        connection = ServerConnection.get_connection(server_ip, username, password)

        command = 'cd ' + bgf_software_path + ' ;ls -ltr | grep -i .rpm'
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        rpm_name = output[-1][:-3]
        log.info('rpm name: %s', rpm_name)
        log.info('command output: %s', command_output)

        log.info('Starting Install of LCM Workflow using rpm bundle')
        Report_file.add_line('Starting Install of LCM Workflow using rpm bundle downloaded')

        command = 'sudo -i wfmgr bundle install --package={}/{}'.format(bgf_software_path, rpm_name)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        command_output = str(stdout.read())
        log.info(command_output)

        if 'already installed' in command_output:
            log.info('LCM Workflow already installed')

        else:
            log.info('waiting for bundle to install ')
            time.sleep(120)
            log.info('LCM workflow deploy is finished using command: %s', command)
            Report_file.add_line('LCM workflow deploy is completed.')

    except Exception as e:
        log.info('Error BGF workflow bundle install on LCM %s', str(e))
        Report_file.add_line('Error BGF workflow bundle install on LCM ' + str(e))
        assert False

    finally:
        connection.close()


def bgf_so_files_transfer():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    bgf_software_path = sit_data._SIT__bgf_software_path
    # so_files_transfer(bgf_software_path)


def generate_ssh_key():
    connection = None
    try:

        ssh_key_generate_on_lcm("")
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        connection = ServerConnection.get_connection(server_ip, username, password)
        vnfd_id = sit_data._SIT__ims_vnfd_id
        ServerConnection.get_file_sftp(connection,
                                       f'/vnflcm-ext/current/vnf_package_repo/{vnfd_id}/'
                                       f'Resources/VnfdWrapperFiles/VNFD_Wrapper.json',
                                       r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_BGF.json')

        file_name = 'VNFD_Wrapper_BGF.json'
        command = 'sudo -i cat /home/jboss_user/.ssh/id_rsa.pub'
        log.info('Executing command: %s', command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        command_output = str(stdout.read())
        key = command_output[2:-5:1]
        log.info('Updating the VNFD_Wrapper.json with id_rsa.pub key %s', key)
        Json_file_handler.update_any_json_attr(Json_file_handler,
                                               r'com_ericsson_do_auto_integration_files/' + file_name,
                                               ['instantiateVnfOpConfig'], 'admin_authorized_key', key)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       r'/home/cloud-user/VNFD_Wrapper.json')

        command = f'sudo -i cp /home/cloud-user/VNFD_Wrapper.json /vnflcm-ext/current/vnf_package_repo/' \
                  f'{vnfd_id}/Resources/VnfdWrapperFiles/VNFD_Wrapper.json'

        log.info('Putting back the VNFD_Wrapper.json after updating the admin_authorized_key %s', command)
        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
        time.sleep(2)

    except Exception as e:
        log.error('Error BGF ssh-key generation %s', str(e))
        Report_file.add_line('Error BGF ssh-key generation ' + str(e))
        assert False

    finally:
        connection.close()


def create_bgf_flavours():
    log.info('Start creating bgf flavors')
    Report_file.add_line('Start creating bgf flavors')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName
    bgf_flavors = sit_data._SIT__bgf_flavors
    flavors_list = bgf_flavors.split(',')
    for flavor_name in flavors_list:

        flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
        if flavor_exists:
            log.info('Flavor %s already exists in CEE', flavor_name)
            Report_file.add_line('Flavor ' + flavor_name + ' already exists in CEE')
        else:
            log.info('Flavor %s does not  exists in CEE', flavor_name)
            Report_file.add_line('Flavor ' + flavor_name + ' does not  exists in CEE')
            name = flavor_name[3:]
            if 'vBGF-6-6-8' in name:
                update_any_flavor_file(name, 8, 6144, 6, tenant_name)
            else:
                log.warn('Flavor name does not match with requirements, '
                         'please check the confluence for BGF deployment %s', flavor_name)
                Report_file.add_line('Flavor name does not match with requirements, '
                                     'please check the confluence for BGF deployment ' + flavor_name)
                assert False

            update_transfer_flavour_file()
            create_flavour('flavour.json', 'flavour_transfer.json', name)

    log.info('Finished creating bgf flavors')
    Report_file.add_line('Finished creating bgf flavors')


def register_bgf_images():
    connection = None
    try:

        log.info('Start register bgf images')
        Report_file.add_line('start register bgf images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        vimzone_name = sit_data._SIT__vimzone_name
        bgf_image_names = sit_data._SIT__bgf_image_names
        bgf_image_ids = sit_data._SIT__bgf_image_ids
        image_names = bgf_image_names.split(',')
        image_ids = bgf_image_ids.split(',')

        for image_name, image_id in zip(image_names, image_ids):
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)
            image_exists = check_image_registered(connection, image_name, token, core_vm_ip)
            if image_exists:
                Report_file.add_line(
                                     'Image with name ' + image_name + ' already registered in cloud manager')
            else:
                log.info('Going to register image with name %s', image_name)
                update_image_file('RegisterImage.json', image_name, vimzone_name, image_id)
                image_registration('RegisterImage.json')

        log.info('Finished register bgf images')
        Report_file.add_line('Finished register bgf images')

    except Exception as e:
        log.error('Error register bgf images %s', str(e))
        Report_file.add_line('Error register bgf images ' + str(e))
        assert False

    finally:
        connection.close()


def update_bgf_node_onboard_file():
    log.info('Connecting with VNF-LCM server')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
    username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    connection = ServerConnection.get_connection(server_ip, username, password)

    path = '/var/tmp/deployBGF/'
    vnfd_id = sit_data._SIT__ims_vnfd_id

    ecm_zip_pacakge = path + vnfd_id + '.zip'

    try:
        log.info('Getting VNFD_Wrapper_BGF.json from server to get onboard params')
        Report_file.add_line(
            'Getting VNFD_Wrapper_BGF.json and vBGF-1.18.zip from server to get onboard params')
        ServerConnection.get_file_sftp(connection,
                                       f'/vnflcm-ext/current/vnf_package_repo/{vnfd_id}\
                                       /Resources/VnfdWrapperFiles/VNFD_Wrapper.json',
                                       r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_BGF.json')
        connection.close()
    except Exception as e:
        log.error('Error while getting the VNFD_Wrapper_BGF.json from server %s', str(e))

    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_BGF.json')

    global package_name
    package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'TEST_BGF_PACKAGE_UPLOAD')
    sit_data._SIT__name = package_name
    log.info('BGF ONBOARD PACKAGE NAME %s', package_name)
    Report_file.add_line('BGF ONBOARD PACKAGE NAME ' + package_name)

    onboard_file_name = 'onboard_bgf.json'
    upload_file = vnfd_id + '.zip'
    update_bgf_onboard_file(r'com_ericsson_do_auto_integration_files/' + onboard_file_name, file_data,
                            package_name)

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    ServerConnection.get_file_sftp(connection, ecm_zip_pacakge,
                                   r'com_ericsson_do_auto_integration_files/' + upload_file)

    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + onboard_file_name,
                                   SIT.get_base_folder(SIT) + onboard_file_name)
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + upload_file,
                                   SIT.get_base_folder(SIT) + upload_file)
    connection.close()


def onboard_bgf_package():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnfd_id = sit_data._SIT__ims_vnfd_id
    upload_file = vnfd_id + '.zip'
    onboard_node_package('onboard_bgf.json', upload_file, package_name)


def verify_bgf_package():
    log.info('start verifying the onboarded bgf package')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

    core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
    # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    vnf_packageId = sit_data._SIT__vnf_packageId
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)

    provisioningStatus, operationalState = get_package_status(connection, token, core_vm_hostname,
                                                              vnf_packageId)

    if 'ACTIVE' in provisioningStatus and 'ENABLED' in operationalState:

        Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
        Report_file.add_line('operationalState is : ' + operationalState)
        log.info('Verification of package uploaded is success')
        Report_file.add_line('Verification of package Upload is success')
        log.info('Finished onboarding package for %s', package_name)
        Report_file.add_line('Finished onboarding package for ' + package_name)
        connection.close()
    else:

        log.error('Verification of package uploaded failed. '
                  'Please check the status of provisioning and operationalState')
        log.error('provisioningStatus: %s    operationalState: %s', provisioningStatus, operationalState)
        Report_file.add_line('Verification of package uploaded failed. '
                             'Please check the status of provisioning and operationalState')
        connection.close()
        assert False


def update_bgf_node_deploy_file():
    connection = None

    log.error('Start updating bgf node deployment file')
    Report_file.add_line('Start updating bgf node deployment file')

    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vnfd_id = sit_data._SIT__ims_vnfd_id
        node_name = vnfd_id + '_' + str(random.randint(0, 999))
        node_name = node_name.replace('.', '_')
        file_name = 'deploy_bgf.json'

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_BGF.json')
        update_bgf_deploy_file(r'com_ericsson_do_auto_integration_files/' + file_name, file_data, node_name)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)
        log.info('Going to start deployment of node %s', node_name)

    except Exception as error:
        log.error('Error updating bgf node deployment file %s ', str(error))
        Report_file.add_line('Error updating bgf node deployment file ' + str(error))
        assert False

    finally:
        connection.close()


def deploy_bgf_package():
    deploy_node('deploy_bgf.json')


def verify_bgf_deployment():
    connection = None
    try:
        log.info('Waiting 60 seconds to verification of node')
        time.sleep(60)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
        node_id = sit_data._SIT__vapp_Id
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)

        # file_data = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_BGF.json')
        # management_ip = file_data['instantiateVnfOpConfig']['management_ip_address']

        # ping_response = get_ping_response(connection, management_ip)

        provisioningStatus, operationalState = get_node_status(connection, token, core_vm_hostname, node_id)

        if 'ACTIVE' == provisioningStatus and 'INSTANTIATED' == operationalState:

            # log.info('Ping Successful')
            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)
            # Report_file.add_line('Ping Successful')
            log.info('Verification of package deployment is success')
            Report_file.add_line('Verification of package deployment is successful')

        else:
            log.info('Verification of package deployment failed. '
                     'Please check the status of provisioning and operationalState and ping response ')
            Report_file.add_line('Verification of package deployment failed. '
                                 'Please check the status of provisioning and operationalState '
                                 'and ping response')
            assert False

    except Exception as e:
        log.error('Error verifying node deployment %s', str(e))
        Report_file.add_line('Error verifying node deployment ' + str(e))
        assert False
    finally:
        connection.close()
