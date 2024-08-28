import json
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *

log = Logger.get_logger('EPG_TOSCA_PREREQUISITE.py')


def prepare_vnfd_package():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    software_path = sit_data._SIT__epgToscaSoftwarePath
    csar_package_name = 'Tosca_EPG_VNFD'
    csar_root_folder = f'{software_path}/VNFD'
    update_yaml_file()
    update_hash_value()
    prepare_csar_package(csar_package_name, csar_root_folder, software_path)


def prepare_csar_package(csar_package_name, csar_package_path, software_path):
    """
        csar_package_path - root folder of the csar package
        software_path - root folder of the software e.g. /var/tmp/deployTOSCAEPG3.14
    """
    try:
        log.info('Start preparing csar package')
        Report_file.add_line('Start preparing csar package')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info(f'Preparing csar package {csar_package_name}')
        Report_file.add_line(f'Preparing csar package {csar_package_name}')

        command1 = f'cd {csar_package_path} && zip -r {csar_package_name}.zip ./ && mv {csar_package_name}.zip ..'
        Report_file.add_line(f'Executing command {command1}')
        stdin, stdout, stderr = connection.exec_command(command1)
        command_output = stdout.read().decode("utf-8")
        Report_file.add_line(command_output)

        error_output = stderr.read().decode("utf-8")
        if error_output:
            log.error("Error message :" + error_output)
            Report_file.add_line(error_output)
            assert False

        log.info('Rename the package ' + csar_package_name)
        Report_file.add_line(f'rename the package {csar_package_name}')
        command2 = f'cd {software_path} && mv {csar_package_name}.zip {csar_package_name}.csar'
        Report_file.add_line(f'Executing command {command2}')

        stdin, stdout, stderr = connection.exec_command(command2)
        command_output = stdout.read().decode("utf-8")
        Report_file.add_line(command_output)

        error_output = stderr.read().decode("utf-8")
        if error_output:
            log.error("Error message :" + error_output)
            Report_file.add_line(error_output)
            assert False

        connection.close()

        log.info(f'Finnished preparing csar package {csar_package_name}')
        Report_file.add_line(f'Finished preparing csar package {csar_package_name}')

    except Exception as e:
        log.error(f'Error preparing csar package {csar_package_name} ' + str(e))
        Report_file.add_line(f'Error preparing csar package {csar_package_name} ' + str(e))
        assert False

    finally:
        try:
            connection.close()
        except Exception as e:
            log.error('Error closing connection' + str(e))
            Report_file.add_line('Error closing connection ' + str(e))


def remove_lcm_entry_epg_tosca():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if 'FALSE' == is_vm_vnfm:
        remove_host_lcm_entry()


def admin_heatstack_rights_epg_tosca():
    update_admin_heatstack_rights()


def update_lcm_password_epg_tosca():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if 'FALSE' == is_vm_vnfm:
        update_lcm_oss_password()


def transfer_workflow_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_tosca_software_path = sit_data._SIT__epgToscaSoftwarePath
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if 'TRUE' == is_vm_vnfm:
        transfer_workflow_rpm_vm_vnfm('EPG_TOSCA', epg_tosca_software_path)
    else:
        transfer_workflow_rpm_vnflcm('EPG_TOSCA', epg_tosca_software_path)


def epg_tosca_workflow_deployment():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_software_path = '/vnflcm-ext/current/vnf_package_repo/'

    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if 'TRUE' == is_vm_vnfm:
        epg_tosca_workflow_deployment_vm_vnfm(epg_software_path)
    else:
        epg_tosca_workflow_deployment_lcm(epg_software_path)


def create_epg_flavours():
    create_epg_tosca_flavours()


def register_epg_images():
    register_epg_tosca_images()


def update_hash_value():
    try:
        log.info('Updating hash value of Definitions/epg.yaml in VNF/epg.mf')
        Report_file.add_line('Updating hash value of Definitions/epg.yaml in VNF/epg.mf')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        software_path = sit_data._SIT__epgToscaSoftwarePath
        csar_root_folder = f'{software_path}/VNFD'

        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        update_hash_script_name = r'update_hash.sh'
        filepath = r'/tmp/'
        source_file_path = r'com_ericsson_do_auto_integration_files/' + update_hash_script_name
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/update_hash.sh',
                                       r'/tmp/update_hash.sh')
        #
        # Updating file permission to shell script
        log.info(f'Changing permission to file {update_hash_script_name}')
        Report_file.add_line(f'Changing permission to file {update_hash_script_name}')
        command1 = f'chmod 744 {filepath}{update_hash_script_name}'
        stdin, stdout, stderr = connection.exec_command(command1)

        log.info(f'Executing script {update_hash_script_name}')
        Report_file.add_line(f'Executing script {update_hash_script_name}')

        command2 = f'cd {filepath}; ./{update_hash_script_name} {csar_root_folder}/epg.mf {csar_root_folder}/Definitions/epg.yaml'
        Report_file.add_line(f'Executing command {command2}')

        stdin, stdout, stderr = connection.exec_command(command2)
        # command_output = stdout.read().decode("utf-8")
        # Report_file.add_line(Report_file, f'Command output {command_output}')

        error_output = stderr.read().decode("utf-8")
        if error_output:
            log.error("Error message :" + error_output)
            Report_file.add_line(error_output)
            assert False

        log.info(f'Deleting script {update_hash_script_name}')
        Report_file.add_line(f'Deleting script {update_hash_script_name}')

        command3 = f'rm {filepath}/{update_hash_script_name}'
        Report_file.add_line(f'Executing command {command3}')
        stdin, stdout, stderr = connection.exec_command(command3)

        error_output = stderr.read().decode("utf-8")
        if error_output:
            log.error("Error message :" + error_output)
            Report_file.add_line(error_output)
            assert False

        log.info('Finished updating hash value of Definitions/epg.yaml')
        Report_file.add_line('Finished updating hash value of Definitions/epg.yaml')

    except Exception as e:

        log.info(f'Error updating hash value using {update_hash_script_name}  ' + str(e))
        Report_file.add_line(f'Error updating hash value using {update_hash_script_name}  ' + str(e))
        assert False

    finally:
        connection.close()


def update_yaml_file():
    try:
        log.info(f'Start updating epg.yaml file')
        Report_file.add_line(f'Start updating epg.yaml file')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        software_path = sit_data._SIT__epgToscaSoftwarePath
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        source_file_path = f'{software_path}/VNFD/Definitions/epg.yaml'
        destination_file_path = r'com_ericsson_do_auto_integration_files/epg.yaml'

        log.info(f'Transferring {source_file_path} to {destination_file_path}')
        Report_file.add_line(f'Transferring {source_file_path} to {destination_file_path}')

        ServerConnection.get_file_sftp(connection, source_file_path, destination_file_path)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        epg_tosca_image_names = sit_data._SIT__epg_tosca_image_names

        attr_list_vrp = ['topology_template', 'node_templates', 'vrp', 'artifacts', 'vrp-image_image']
        attr_list_vsfo_pp = ['topology_template', 'node_templates', 'vsfo-pp', 'artifacts', 'vsfo-image_image']
        attr_list_vsfo_cp = ['topology_template', 'node_templates', 'vsfo-cp', 'artifacts', 'vsfo-image_image']

        urls = []
        file_name = r'com_ericsson_do_auto_integration_files/epg.yaml'

        epg_tosca_image_names_list = list(epg_tosca_image_names.split(","))

        for name in epg_tosca_image_names_list:
            log.info("Processing image: " + str(name))
            Report_file.add_line("Processing image: " + str(name))

            url = get_image_url(name)

            log.info("image URL: " + str(url))
            Report_file.add_line("image URL: " + str(url))

            if 'epg_vrp' in name:
                Json_file_handler.update_fifth_attr_yaml(Json_file_handler, file_name, attr_list_vrp[0],
                                                         attr_list_vrp[1],
                                                         attr_list_vrp[2],
                                                         attr_list_vrp[3], attr_list_vrp[4], 'file', url)
            elif 'epg_vsfo' in name:
                Json_file_handler.update_fifth_attr_yaml(Json_file_handler, file_name, attr_list_vsfo_pp[0],
                                                         attr_list_vsfo_pp[1],
                                                         attr_list_vsfo_pp[2],
                                                         attr_list_vsfo_pp[3], attr_list_vsfo_pp[4], 'file', url)
                Json_file_handler.update_fifth_attr_yaml(Json_file_handler, file_name, attr_list_vsfo_cp[0],
                                                         attr_list_vsfo_cp[1],
                                                         attr_list_vsfo_cp[2],
                                                         attr_list_vsfo_cp[3], attr_list_vsfo_cp[4], 'file', url)
            else:
                log.info("No suitable image found")
                Report_file.add_line("no suitable image found")

            urls.append(url)

        source_file_path = r'com_ericsson_do_auto_integration_files/epg.yaml'
        destination_file_path = f'{software_path}/VNFD/Definitions/epg.yaml'

        log.info(f'Transferring {source_file_path} to {destination_file_path}')
        Report_file.add_line(f'Transferring {source_file_path} to {destination_file_path}')

        ServerConnection.put_file_sftp(connection, source_file_path, destination_file_path)

        log.info(f'Finished updating epg.yaml file')
        Report_file.add_line(f'Finished updating epg.yaml file')

    except Exception as e:

        log.info(f'Error updating epg.yaml file ' + str(e))
        Report_file.add_line(f'Error updating epg.yaml file  ' + str(e))
        assert False

    finally:
        try:
            connection.close()
        except Exception as e:
            log.info(f'Error closing connection ' + str(e))
            Report_file.add_line(f'Error closing connection  ' + str(e))


def get_image_url(image_name):
    try:

        log.info('Starting to get image url')
        Report_file.add_line('Starting to get image url')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_ip)

        command = f'''curl --insecure "https://{core_vm_hostname}/ecm_service/images" -H "Accept: application/json" -H "AuthToken: {token}"'''

        log.info(f'Executing curl command {command}')
        Report_file.add_line(f'Executing curl command {command}')

        stdin, stdout, stderr = connection.exec_command(command)
        command_output = stdout.read().decode("utf-8")

        full_dict = json.loads(command_output)
        image_dict = full_dict['data']

        images_list = list(image_dict.values())
        images = images_list[0]

        for image in images:
            if image['name'] == image_name:
                return image["url"]

        log.info('Finished getting image url')
        Report_file.add_line('Finished getting image url')

    except Exception as e:
        log.info(f'Error getting image url ' + str(e))
        Report_file.add_line(f'Error getting image url  ' + str(e))
        assert False
