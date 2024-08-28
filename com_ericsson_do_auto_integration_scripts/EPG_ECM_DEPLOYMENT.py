import time

from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import check_flavor_exists
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (
    vm_vnfm_lcm_workflow_installation_validation, LCM_workflow_installation_validation,
    update_workflow_package_hot_vm_vnfm, update_workflow_package_hot, deploy_node,
    onboard_node_package, ssh_key_generate_on_lcm, unpack_node_software, transfer_node_software_vm_vnfm,
    transfer_node_software, update_lcm_oss_password, remove_host_lcm_entry, check_image_registered,
    update_admin_heatstack_rights, get_file_name_from_vm_vnfm, create_ns_ecm, instantiate_ns_ecm
)
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import (
    create_flavour, image_registration
)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import fetch_external_subnet_id
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import (
    get_package_status, get_ping_response, get_node_status, check_lcm_workflow_status, check_enm_node_sync
)
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import chown_and_file_permission, \
    get_VMVNFM_host_connection, get_vmvnfm_pod_cmd
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import (
    update_any_flavor_file, update_transfer_flavour_file, update_image_file
)
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (
    update_epg_deploy_file, update_epg_onboard_file, update_runtime_env_file, update_tosca_epg_instantiate_file,
    update_etsi_tepg_instanatiate_file)
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details

log = Logger.get_logger('EPG_ECM_DEPLOYMENT.py')

package_name = ''
epg_zip_package = ''


def remove_LCM_entry():
    remove_host_lcm_entry()


def admin_heatstack_rights():
    update_admin_heatstack_rights()


def update_lcm_password():
    update_lcm_oss_password()


def transfer_epg_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_software_path = sit_data._SIT__epgSoftwarePath
    epg_version = sit_data._SIT__epgVersion
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if epg_version == 'EPG3.6':

        hot_file = 'vEPG3.hot.yaml'

    else:

        hot_file = 'template.yaml'

    if 'TRUE' == is_vm_vnfm:
        transfer_node_software_vm_vnfm('EPG', epg_software_path, epg_version)
    else:
        transfer_node_software('EPG', epg_software_path, epg_version, hot_file)


def unpack_epg_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_version = sit_data._SIT__epgVersion
    if epg_version == 'EPG3.6':

        hot_file = 'vEPG3.hot.yaml'

    else:

        hot_file = 'template.yaml'

    unpack_node_software('EPG', epg_version, 'EPG_Software_complete.tar', 'EPG_Software_resources.tar', hot_file)


def workflow_deployment():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_version = sit_data._SIT__epgVersion
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    epg_software_path = r'/vnflcm-ext/current/vnf_package_repo/' + epg_version
    if 'TRUE' == is_vm_vnfm:
        epg_workflow_deployment_vm_vnfm(epg_software_path)
    else:
        epg_workflow_deployment(epg_software_path)


def epg_workflow_deployment(epg_software_path):
    try:
        log.info('start EPG workflow bundle install on LCM')
        Report_file.add_line('EPG Workflow  bundle install on LCM begins...')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        connection = ServerConnection.get_connection(server_ip, username, password)

        command = 'cd ' + epg_software_path + ' ;ls -ltr | grep -i .rpm'
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        output = command_output.split()
        rpm_name = output[-1][:-3]
        log.info('rpm name :' + rpm_name)
        log.info('command output  : ' + command_output)

        command = 'sudo -i wfmgr bundle install --package={}/{}'.format(epg_software_path, rpm_name)

        LCM_workflow_installation_validation(connection, command, 'EPG')

        update_workflow_package_hot(connection, password)

        log.info(
            'Starting to transfer _ericsson_templ.xml_ file used to generate the HOT package to the fullConfiguration directory')
        Report_file.add_line(
            'Starting to transfer _ericsson_templ.xml_ file used to generate the HOT package to the fullConfiguration directory')

        command = 'cd ' + epg_software_path + ';cp ericsson_templ.xml /vnflcm-ext/ericsson/ERICepg_lcm_wf_heatworkflows/work/vnf-configurations/fullConfiguration/'
        log.info('Command to copy xml file :' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        log.info(
            'waiting 80 seconds to copy ericsson_templ.xml to /vnflcm-ext/ericsson/ERICepg_lcm_wf_heatworkflows/work/vnf-configurations/fullConfiguration/')
        time.sleep(80)

        log.info(
            'Finished  to transfer _ericsson_templ.xml_ file used to generate the HOT package to the fullConfiguration directory')
        Report_file.add_line(
            'Finished to transfer _ericsson_templ.xml_ file used to generate the HOT package to the fullConfiguration directory')

        connection.close()
    except Exception as e:
        connection.close()
        log.error('Error EPG workflow bundle install on LCM ' + str(e))
        Report_file.add_line('Error EPG workflow bundle install on LCM ' + str(e))
        assert False


def epg_tosca_workflow_deployment_lcm(epg_software_path):
    try:
        log.info('start EPG workflow bundle install on LCM')
        Report_file.add_line('EPG Workflow  bundle install on LCM begins...')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        connection = ServerConnection.get_connection(server_ip, username, password)

        command = f"ls -l {epg_software_path}| grep -i rpm | awk '{{print $9}}'"
        stdin, stdout, stderr = connection.exec_command(command)
        rpm_name = stdout.read().decode("utf-8").strip()

        handle_stderr(stderr, log)

        log.info(f'rpm name: {rpm_name}')
        Report_file.add_line(f'rpm name: {rpm_name}')

        command = 'sudo -i wfmgr bundle install --package={}/{}'.format(epg_software_path, rpm_name)

        LCM_workflow_installation_validation(connection, command, 'EPG_TOSCA')

        log.info('Finished EPG workflow bundle install on LCM')
        Report_file.add_line('Finished EPG workflow bundle install on LCM')

    except Exception as e:
        log.error('Error EPG workflow bundle install on LCM ' + str(e))
        Report_file.add_line('Error EPG workflow bundle install on LCM ' + str(e))
        assert False
    finally:
        connection.close()


def epg_tosca_workflow_deployment_vm_vnfm(epg_software_path):
    try:
        log.info('start EPG Tosca workflow bundle install on VM-VNFM')
        Report_file.add_line('start EPG Tosca workflow bundle install on VM-VNF')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        dir_connection = get_VMVNFM_host_connection()

        rpm_file = get_file_name_from_vm_vnfm(dir_connection, '.rpm', epg_software_path)

        cmd = f"sudo -E wfmgr bundle install --package={epg_software_path}/{rpm_file}"
        command = get_vmvnfm_pod_cmd(cmd)

        vm_vnfm_lcm_workflow_installation_validation(dir_connection, command, 'EPG_TOSCA')

        log.info('Finished EPG Tosca workflow bundle install on VM-VNFM')

    except Exception as e:

        log.error('Error EPG workflow bundle install on VM-VNFM ' + str(e))
        Report_file.add_line('Error EPG workflow bundle install on VM-VNFM' + str(e))
        assert False
    finally:
        dir_connection.close()


def epg_workflow_deployment_vm_vnfm(epg_version):
    try:
        log.info('start EPG workflow bundle install on VM-VNFM')
        Report_file.add_line('start EPG workflow bundle install on VM-VNF')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vnfd_id = epg_version
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        dir_connection = get_VMVNFM_host_connection()

        path = vnfd_id
        rpm_file = get_file_name_from_vm_vnfm(dir_connection, '.rpm', path)
        cmd = f"sudo -E wfmgr bundle install --package={path}/{rpm_file}"
        command = get_vmvnfm_pod_cmd(cmd)

        vm_vnfm_lcm_workflow_installation_validation(dir_connection, command, 'EPG')

        update_workflow_package_hot_vm_vnfm(dir_connection, vm_vnfm_namespace)

        time.sleep(2)

        log.info(
            'transfering xml to /vnflcm-ext/ericsson/ERICepg_lcm_wf_heatworkflows/work/vnf-configurations/fullConfiguration/ ')

        xml_file = get_file_name_from_vm_vnfm(dir_connection, '.xml', path)
        cmd = f"cp {path}/{xml_file} /vnflcm-ext/ericsson/ERICepg_lcm_wf_heatworkflows/work/vnf-configurations/fullConfiguration/{xml_file}"
        command = get_vmvnfm_pod_cmd(cmd)

        Report_file.add_line('Command :' + command)

        stdin, stdout, stderr = dir_connection.exec_command(command)

        time.sleep(5)
        xml_path = f'/vnflcm-ext/ericsson/ERICepg_lcm_wf_heatworkflows/work/vnf-configurations/fullConfiguration/{xml_file}'
        chown_and_file_permission(dir_connection, xml_path, "777", "jboss_user", recursive=False)

        log.info('file transfered sucessfully ..')

    except Exception as e:

        log.error('Error EPG workflow bundle install on VM-VNFM ' + str(e))
        Report_file.add_line('Error EPG workflow bundle install on VM-VNFM' + str(e))
        assert False
    finally:
        dir_connection.close()


def generate_ssh_key():
    ssh_key_generate_on_lcm()


def create_epg_flavours():
    log.info('start creating epg flavors')
    Report_file.add_line('start creating epg flavors')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName
    epg_flavors = sit_data._SIT__epg_flavors
    flavors_list = epg_flavors.split(',')
    for flavor_name in flavors_list:

        flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
        if flavor_exists:
            log.info('Flavor with name ' + flavor_name + ' already exists in CEE')
            Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in CEE')
        else:
            log.info('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            name = flavor_name[3:]
            if '2vcpu' in name:
                update_any_flavor_file(name, 2, 6144, 40, tenant_name)
                update_transfer_flavour_file()
            elif '8vcpu' in name:
                update_any_flavor_file(name, 8, 16384, 40, tenant_name)
                update_transfer_flavour_file()
            else:
                log.warn(
                    'Flavor name does not match with requirements , please check the confluence for EPG deployment ' + flavor_name)
                Report_file.add_line(
                    'Flavor name does not match with requirements , please check the confluence for EPG deployment ' + flavor_name)
                assert False

            create_flavour('flavour.json', 'flavour_transfer.json', name)

    log.info('Finished creating epg flavors')
    Report_file.add_line('Finished creating epg flavors')


def create_epg_tosca_flavours():
    log.info('start creating epg flavors')
    Report_file.add_line('start creating epg flavors')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName
    epg_flavors = sit_data._SIT__epg_tosca_flavors
    flavors_list = epg_flavors.split(',')
    for flavor_name in flavors_list:

        flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
        if flavor_exists:
            log.info('Flavor with name ' + flavor_name + ' already exists in CEE')
            Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in CEE')
        else:
            log.info('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in CEE')
            name = flavor_name.strip()[3:]

            if '2vcpu' in name:
                update_any_flavor_file(name, 2, 6144, 40, tenant_name)
                update_transfer_flavour_file()
            elif '6vcpu' in name:
                update_any_flavor_file(name, 6, 16384, 40, tenant_name)
                update_transfer_flavour_file()
            elif '8vcpu' in name:
                update_any_flavor_file(name, 8, 16384, 40, tenant_name)
                update_transfer_flavour_file()
            else:
                log.warn(
                    'Flavor name does not match with requirements , please check the confluence for EPG deployment ' + flavor_name)
                Report_file.add_line(
                    'Flavor name does not match with requirements , please check the confluence for EPG deployment ' + flavor_name)
                assert False

            create_flavour('flavour.json', 'flavour_transfer.json', name)

    log.info('Finished creating epg flavors')
    Report_file.add_line('Finished creating epg flavors')


def register_epg_images():
    try:

        log.info('start register epg images')
        Report_file.add_line('start register epg images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vimzone_name = sit_data._SIT__vimzone_name
        epg_image_names = sit_data._SIT__epg_image_names
        epg_image_ids = sit_data._SIT__epg_image_ids
        image_names = epg_image_names.split(',')
        image_ids = epg_image_ids.split(',')

        for image_name, image_id in zip(image_names, image_ids):
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username,
                                                         ecm_password)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
            image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
            if image_exists:
                Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
            else:
                log.info('Going to register image with name ' + image_name)
                update_image_file('RegisterImage.json', image_name, vimzone_name, image_id)
                image_registration('RegisterImage.json')

        log.info('Finished register epg images')
        Report_file.add_line('Finished register epg images')
        connection.close()

    except Exception as e:
        connection.close()
        log.error('Error register epg images ' + str(e))
        Report_file.add_line('Error register epg images ' + str(e))
        assert False


def register_epg_tosca_images():
    try:

        log.info('start register epg images')
        Report_file.add_line('start register epg images')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vimzone_name = sit_data._SIT__vimzone_name
        epg_image_names = sit_data._SIT__epg_tosca_image_names
        epg_image_ids = sit_data._SIT__epg_tosca_image_ids
        image_names = epg_image_names.split(',')
        image_ids = epg_image_ids.split(',')

        for image_name, image_id in zip(image_names, image_ids):
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username,
                                                         ecm_password)
            token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
            image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
            if image_exists:
                Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
            else:
                log.info('Going to register image with name ' + image_name)
                update_image_file('RegisterImage.json', image_name, vimzone_name, image_id)
                image_registration('RegisterImage.json')

        log.info('Finished register epg images')
        Report_file.add_line('Finished register epg images')
        connection.close()

    except Exception as e:
        connection.close()
        log.error('Error register epg images ' + str(e))
        Report_file.add_line('Error register epg images ' + str(e))
        assert False


def update_onboard_file():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_software_path = sit_data._SIT__epgSoftwarePath
    node_version = sit_data._SIT__epgVersion
    generic_update_onboard_file(epg_software_path, node_version)


def generic_update_onboard_file(epg_software_path, node_version):
    log.info('Connecting with VNF-LCM server')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    path = epg_software_path + '/' + node_version
    global epg_zip_package
    epg_zip_package = node_version + '.zip'
    log.info('Getting VNFD_Wrapper_EPG.json and {} from server to get onboard params'.format(epg_zip_package))
    Report_file.add_line(
        'Getting VNFD_Wrapper_EPG.json and {} from server to get onboard params'.format(epg_zip_package))
    global package_name
    if 'TRUE' == is_vm_vnfm:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'VNFM_EPG')

        ServerConnection.get_file_sftp(connection, path + '/Resources/VnfdWrapperFiles/VNFD_Wrapper_EPG.json',
                                       r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
        ServerConnection.get_file_sftp(connection, path + '/' + epg_zip_package,
                                       r'com_ericsson_do_auto_integration_files/' + epg_zip_package)


    else:

        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
        # todo if old EPG and new EPG run in parallel then below epg name should be changed
        package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'TEST_EPG')

        try:

            ServerConnection.get_file_sftp(connection,
                                           r'/vnflcm-ext/current/vnf_package_repo/' + node_version + '/Resources/VnfdWrapperFiles/VNFD_Wrapper_EPG.json',
                                           r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
            ServerConnection.get_file_sftp(connection,
                                           r'/vnflcm-ext/current/vnf_package_repo/' + node_version + '/' + epg_zip_package,
                                           r'com_ericsson_do_auto_integration_files/' + epg_zip_package)

        except Exception as e:
            log.error(
                'Error while getting the VNFD_Wrapper_EPG.json or {} from server Error : {} '.format(epg_zip_package,
                                                                                                     str(e)))

    connection.close()

    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')

    sit_data._SIT__name = package_name
    log.info('EPG ONBOARD PACKAGE NAME ' + package_name)
    Report_file.add_line('EPG ONBOARD PACKAGE NAME ' + package_name)

    onboard_file_name = 'onboard_epg.json'
    upload_file = epg_zip_package
    update_epg_onboard_file(r'com_ericsson_do_auto_integration_files/' + onboard_file_name, file_data, package_name)

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + onboard_file_name,
                                   SIT.get_base_folder(SIT) + onboard_file_name)
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + upload_file,
                                   SIT.get_base_folder(SIT) + upload_file)
    connection.close()


def onboard_epg_package():
    # todo two EPGs cannot run in parallel, discuss with Shajun about runtime file
    onboard_node_package('onboard_epg.json', epg_zip_package, package_name)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnfPackage_id = sit_data._SIT__vnf_packageId
    update_runtime_env_file('EPG_PACKAGE_ID', vnfPackage_id)


def verify_epg_package():
    log.info('start verifying the onboarded epg package')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

    core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    vnf_packageId = sit_data._SIT__vnf_packageId
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


def update_deploy_file_epg_ecm():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    node_version = sit_data._SIT__epgVersion
    # node_name = node_version+'_' + str(random.randint(0, 999))
    # node_name = node_name.replace('.','_')
    package_name = sit_data._SIT__name
    node_name = package_name
    file_name = 'deploy_epg.json'

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
    update_epg_deploy_file(r'com_ericsson_do_auto_integration_files/' + file_name, file_data, node_name)
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                   SIT.get_base_folder(SIT) + file_name)
    log.info('Going to start deployment of node ' + node_name)
    connection.close()


def deploy_epg_package():
    deploy_node('deploy_epg.json')


def verify_epg_deployment():
    try:

        log.info('waiting 180 seconds to verification of node')
        time.sleep(180)
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
                                                    r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
        ip_address = file_data['instantiateVnfOpConfig']['vnfIpAddress']
        ping_response = get_ping_response(connection, ip_address)

        provisioningStatus, operationalState = get_node_status(connection, token, core_vm_hostname, node_id)

        if 'ACTIVE' == provisioningStatus and 'INSTANTIATED' == operationalState and True == ping_response:

            log.info('Ping Successful')
            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)
            Report_file.add_line('Ping Successful')
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


def get_tosca_epg_param_file():
    """
    This file is required to fetch vnf addition param attributes to update instantiate file
    we can get IP address of node from this file for verification
    """
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        source_path = f'{SIT.get_epg_tosca_software_path(SIT)}/so-artifacts'
        log.info('Getting vnfAdditionalParamTEPG.json file from blade software path %s', source_path)
        vnf_param_file = 'vnfAdditionalParamTEPG.json'
        ServerConnection.get_file_sftp(connection, f'{source_path}/{vnf_param_file}',
                                       r'com_ericsson_do_auto_integration_files/' + vnf_param_file)


    except Exception as e:
        log.error('Error fetching param file from blade %s ', str(e))
        assert False
    finally:
        if connection:
            connection.close()


def create_tosca_epg_ns():
    create_ns_ecm("tosca-epg", "TOSCA_EPG_NS_INSTANCE_ID")


def instantiate_tosca_epg_ns():
    file_name = 'tosca_epg_ns_instance.json'
    get_tosca_epg_param_file()
    external_network_id, sub_network_id, external_network_system_id, sub_network_system_id = fetch_external_subnet_id()
    global vapp_name
    vapp_name = Common_utilities.get_name_with_timestamp(Common_utilities, "tosca-epg")
    update_runtime_env_file('TOSCA_EPG_VAPP', vapp_name)
    update_tosca_epg_instantiate_file(file_name, vapp_name, external_network_system_id, sub_network_system_id)
    instantiate_ns_ecm("tosca-epg", file_name)


def create_etsi_tepg_ns():
    create_ns_ecm("etsi-tosca-epg", "ETSI_TEPG_NS_INSTANCE_ID")


def instantiate_etsi_tepg_ns():
    file_name = 'instantiate_etsi_tepg.json'
    global vapp_name
    vapp_name = Common_utilities.get_name_with_timestamp(Common_utilities, "etsi-tosca-epg")
    update_runtime_env_file('ETSI_TOSCA_EPG_VAPP', vapp_name)
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    epg_software_path = SIT.get_epg_etsi_nsd_software_path(SIT)
    node_version = SIT.get_epg_etsi_nsd_version(SIT)
    path = f'{epg_software_path}/{node_version}'
    ServerConnection.get_file_sftp(connection, f'{path}/Resources/VnfdWrapperFiles/VNFD_Wrapper_EPG.json',
                                   'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
    update_etsi_tepg_instanatiate_file(file_name, vapp_name, file_data)
    instantiate_ns_ecm("etsi-tosca-epg", file_name)


def eocm_epg_tosca_lcm_workflow_status():
    node_defination_name = 'Instantiate VNF'
    check_lcm_workflow_status(vapp_name, node_defination_name)


def eocm_epg_etsi_tosca_lcm_workflow_status():
    node_defination_name = 'Instantiate vEPG on OpenStack'
    check_lcm_workflow_status(vapp_name, node_defination_name)


def eocm_epg_tosca_enm_sync_status():
    check_enm_node_sync(vapp_name)
