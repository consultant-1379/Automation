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
import ast
import time
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_vnflaf_yaml_scalefiles,
                                                                         update_VNFD_wrapper_SCALE_OUT,
                                                                         update_VNFD_wrapper_SCALE_IN)
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.ETSI_TOSCA_DUMMY_DEPLOYMENT import update_VNFD_wrapper_HEAL
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import (verify_worklow_version,
                                                                                    fetch_external_management_id)
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import (get_VMVNFM_host_connection,
                                                                         transfer_director_file_to_vm_vnfm,
                                                                         chown_and_file_permission)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (get_node_vnf_vapp_id_ECM,
                                                                          check_image_registered,
                                                                          get_image_vimobjectId)

log = Logger.get_logger('SCALE_HEAL.py')
vnf_instance_id = ''
onboard_package_name = ''
vnf_manager_id = ''
vnf_manager_name = ''


def transfer_scale_files(config_files, scale_option):
    """
    Inputs:
        files: List of scale config(xml) files
        scale_option: EPG_TOSCA_SCALE_HEAL/EPG_SCALE_HEAL
    Output:
        Transfer scale config files from local to ccd then to vnflcm
    """
    dir_conn, connection = None, None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(
            Server_details)
        if scale_option == "EPG_TOSCA_SCALE_HEAL":
            scale_file_path = SIT.get_epg_tosca_software_path(SIT)
        elif scale_option == "EPG_SCALE_HEAL":
            scale_file_path = SIT.get_epg_software_path(SIT)

        for file in config_files:
            connection = ServerConnection.get_connection(
                ecm_server_ip, ecm_username, ecm_password)
            log.info('Start transfering %s file to vm vnfm', file)
            vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
            if vm_vnfm_namespace == 'eo-deploy':
                private_key_file = "eccd-2-3.pem"
            else:
                private_key_file = 'eccd150-director-key'

            # First transferring file from blade to director
            vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(
                Server_details)
            source_path = f'{scale_file_path}/{file}'
            destination_path = f'/home/{Ecm_core.get_vm_vnfm_director_username(Ecm_core)}/'
            ServerConnection.transfer_files_with_an_encrypted_pem_file(connection, private_key_file,
                                                                       source_path, vm_vnfm_director_username,
                                                                       vm_vnfm_director_ip, destination_path)

        # Now transfer files from eccd home folder to VMVNFM
        dir_conn = get_VMVNFM_host_connection()
        for file in config_files:
            source = f'/home/{Ecm_core.get_vm_vnfm_director_username(Ecm_core)}/{file}'
            if scale_option == "EPG_TOSCA_SCALE_HEAL":
                vapp_name = SIT.get_tosca_epg_vapp(SIT)
                external_system_id = fetch_external_management_id(vapp_name)
                if not external_system_id:
                    log.error('External system id is None. Check if EPG has been deployed properly')
                    assert False
                vnf_instance_folder = '/vnflcm-ext/current/vnf_instances/'
                destination_folder = vnf_instance_folder + external_system_id + '/'
                chown_and_file_permission(dir_conn, vnf_instance_folder, "777", "jboss_user")
                # updating as part of SM-139566
                # chown_and_file_permission(dir_conn, destination_folder, "777", "jboss_user")
            elif scale_option == "EPG_SCALE_HEAL":
                vapp_name = SIT.get_epg_vapp_name(SIT)
                destination_folder = f'''/vnflcm-ext/ericsson/ERICepg_lcm_wf_heatworkflows/work/vnf_catalog/{vapp_name}/configuration_files/'''
                chown_and_file_permission(dir_conn, destination_folder, "777", "jboss_user")
            destination_file = destination_folder + file
            transfer_director_file_to_vm_vnfm(dir_conn, source, destination_file)
            chown_and_file_permission(dir_conn, destination_file, "777", "jboss_user", recursive=False)

    except Exception as err:
        log.error('Transferring of scale config files %s failed due to %s', ",".join(config_files), str(err))
        assert False
    finally:
        connection.close()
        if dir_conn:
            dir_conn.close()


def lcm_transfer_scale_files(config_files, scale_option):
    """
    Inputs:
        config_files: List of scale config(xml) files
        scale_option: EPG_TOSCA_SCALE_HEAL/EPG_SCALE_HEAL
    Output:
        Transfer scale config files from local to ccd then to vnflcm
    """
    lcm_conn, connection = None, None
    try:
        log.info('making connection with LCM for scale operation ')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        lcm_conn = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
        for file in config_files:
            log.info('Start transferring scale xml file %s', file)
            file_path = f'/{ecm_username}/'
            if scale_option == "EPG_SCALE_HEAL":
                epg_vapp_name = SIT.get_epg_vapp_name(SIT)
                epg_software_path = SIT.get_epg_software_path(SIT)
                source_path = f'{epg_software_path}/{file}'
                destination_path = f'''/vnflcm-ext/ericsson/ERICepg_lcm_wf_heatworkflows/work/vnf_catalog/{epg_vapp_name}/configuration_files/{file}'''
            elif scale_option == "EPG_TOSCA_SCALE_HEAL":
                epg_tosca_software_path = SIT.get_epg_tosca_software_path(SIT)
                source_path = f'{epg_tosca_software_path}/{file}'
                destination_path = f'/home/{lcm_username}/{file}'

            ServerConnection.transfer_folder_between_remote_servers(connection, lcm_server_ip, lcm_username,
                                                                    lcm_password, source_path,
                                                                    destination_path, file_path, 'put')

            if scale_option == "EPG_SCALE_HEAL":
                command = 'cd' + destination_path + ';chown jboss_user:jboss epg_vsfo_cp3.xml'
                Report_file.add_line('Permission Command - ' + command)
            elif scale_option == "EPG_TOSCA_SCALE_HEAL":
                source_path = f'/home/{lcm_username}/{file}'
                vapp_name = SIT.get_tosca_epg_vapp(SIT)
                external_system_id = fetch_external_management_id(vapp_name)
                if not external_system_id:
                    log.error('External system id is None. Check if EPG has been deployed properly')
                    assert False
                destination_path = f'/vnflcm-ext/current/vnf_instances/{external_system_id}/{file}'
                command = (f'echo {lcm_password} | sudo -S chown jboss_user:jboss {source_path} && '
                           f'echo {lcm_password} | sudo -S mv {source_path} {destination_path}')

            log.info('Executing command: %s', command)
            stdin, stdout, stderr = lcm_conn.exec_command(command, get_pty=True)
            time.sleep(3)
            handle_stderr(stderr, log)
            log.info('Closing lcm connection')
            log.info('file %s transferred successfully', file)
    except Exception as error:
        log.error('Error in scale xml file transfer %s', str(error))
        assert False
    finally:
        connection.close()
        if lcm_conn:
            lcm_conn.close()


def fetch_vapp_instance_id(connection, environment, option):
    data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
    source = r'/root/' + 'run_time_' + environment + '.json'
    ServerConnection.get_file_sftp(connection, source, data_file)
    if option == "EPG_SCALE_HEAL":
        onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                     'ONBOARD_EPG_PACKAGE')
    elif option == "EPG_TOSCA_SCALE_HEAL":
        onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                     'TOSCA_EPG_VAPP')
    else:
        onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_PACKAGE')
    log.info('Going to fetch Vapp id for ' + onboard_package_name)
    connection.close()
    global vapp_id
    vapp_id, vnf_id = get_node_vnf_vapp_id_ECM(onboard_package_name)


def fetch_vnf_instance_id(connection, enm_token, enm_host_name, environment, option=''):
    log.info('Start fetching vnf_instance_id')

    global vnf_manager_id, vnf_manager_name, onboard_package_name
    data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
    source = r'/root/' + 'run_time_' + environment + '.json'
    ServerConnection.get_file_sftp(connection, source, data_file)

    if option == "EPG_SCALE_HEAL":
        onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                     'ONBOARD_EPG_PACKAGE')

    elif option == 'TOSCA-EPG-HEAL':
        onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                     'ONBOARD_EPG_TOSCA_PACKAGE')

    else:
        onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_PACKAGE')

    vnf_manager_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VNF_MANAGER_ID')
    vnf_manager_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VNF_MANAGER_NAME')

    log.info('onboard package name: %s', onboard_package_name)
    log.info('vnf manager id: %s', vnf_manager_id)
    log.info('vnf manager name: %s', vnf_manager_name)

    curl = '''curl -k --cookie "iPlanetDirectoryPro={}" -H "Accept: application/json" 'https://{}/vnflcm/v1/vnf_instances{}'''.format(
        enm_token, enm_host_name, "'")
    command = curl.replace('\n', '')
    log.info(command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)

    command_out = ExecuteCurlCommand.get_output_replace_braces(command_output)

    log.info('Command output: %s', command_out)
    output = ast.literal_eval(command_out)

    log.info('Output: %s', output)

    for count in range(len(output)):
        item = output[count]
        state = item['instantiationState']
        package_name = item['vnfInstanceName']
        if 'INSTANTIATED' == state and onboard_package_name == package_name:
            vnf_id = item['id']
            log.info('id of vnf: %s', vnf_id)
            global vnf_instance_id
            vnf_instance_id = vnf_id
            break

    if vnf_instance_id == '':
        log.info('Instantiated vnf_instance_id is not found')
        assert False


def fetch_evnfm_instance_id(connection, evnfm_token, evnfm_hostname, option=''):
    log.info('Start fetching evnfm vnf_instance_id')

    global vm_vnfm_manager_id, vm_vnfm_name, dummy_package_name
    environment = Server_details.ecm_host_blade_env(Server_details)
    data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
    source = r'/root/' + 'run_time_' + environment + '.json'
    ServerConnection.get_file_sftp(connection, source, data_file)

    if option == 'EPG-HEAL':
        dummy_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                   'ONBOARD_EPG_PACKAGE')
    elif option == 'TOSCA-EPG-HEAL':
        dummy_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                   'TOSCA_EPG_VAPP')
    else:
        dummy_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                   'ONBOARD_PACKAGE')

    vm_vnfm_manager_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                               'VM_VNFM_MANAGER_ID')
    vm_vnfm_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VM_VNMF_MANAGER_NAME')

    log.info('dummy onboard package name: %s', dummy_package_name)
    log.info('vm vnfm manager id: %s', vm_vnfm_manager_id)
    log.info('vm vnfm manager name: %s', vm_vnfm_name)

    command = f'curl --insecure -H "cookie: JSESSIONID={evnfm_token}" -H "Accept: */*" ' \
              f'https://{evnfm_hostname}/vnflcm/v1/vnf_instances?nextpage_opaque_marker=vmvnfm'
    log.info('curl for fetching vnf instances: %s', command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    output = ast.literal_eval(command_out)

    for count in range(len(output)):
        item = output[count]
        state = item['instantiationState']
        package_name = item['vnfInstanceName']
        if 'INSTANTIATED' == state and dummy_package_name == package_name:
            id = item['id']
            log.info('id of vnf: %s', id)
            global evnfm_vnf_instance_id
            evnfm_vnf_instance_id = id
            break

    if evnfm_vnf_instance_id == '':
        log.info('Instantiated vnf_instance_id is not found')
        assert False


def fetch_image_exists_in_ECM():
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
    image_name = 'ERICrhelvnflafimage'
    image_exists = check_image_registered(connection, image_name, token, core_vm_hostname,
                                          transfered_to_vim=True)


def get_flavor_name_and_vimobjectId():
    servicesImage = get_image_vimobjectId()
    tosca_dummy_depl_flavor = 'CM-Vnflaf_Etsi_Tosca_Dummy_Flavor'
    return servicesImage, tosca_dummy_depl_flavor


def start_scale_out(node_name=''):
    try:
        log.info('Start ScaleOut ')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        environment = Server_details.ecm_host_blade_env(Server_details)
        enm_hostname, enm_username, enm_password = Server_details.enm_host_server_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        external_ip_for_services_vm_scale = sit_data._SIT__externalIpForServicesVmToScale
        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
        vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(
            Server_details)
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        if node_name == 'TOSCA_DUMMY':
            file_name = r'vnflaf_cee-env.yaml'
            fetch_image_exists_in_ECM()
            servicesImage, tosca_dummy_depl_flavor = get_flavor_name_and_vimobjectId()
            file_path = 'com_ericsson_do_auto_integration_files/vnflaf/Resources/EnvironmentFiles/'
            update_vnflaf_yaml_scalefiles(file_path, file_name, servicesImage, tosca_dummy_depl_flavor,
                                          'Scale-Out')
        else:
            file_name = r'VNFD_Wrapper_VNFLAF.json'
            file_path = 'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/'
            update_VNFD_wrapper_SCALE_OUT(file_name)

        if 'TRUE' == is_vm_vnfm:
            log.info('nested connection open scale out')
            dir_connection = get_VMVNFM_host_connection()
            source_filepath = file_path + file_name
            ServerConnection.put_file_sftp(dir_connection, source_filepath,
                                           r'/home/' + vm_vnfm_director_username + '/' + file_name)

            source = '/home/{}/{}'.format(vm_vnfm_director_username, file_name)
            if node_name == 'TOSCA_DUMMY':
                destination = '/vnflcm-ext/current/vnf_package_repo/vnflaf/HOT/Resources/EnvironmentFiles/vnflaf_cee-env.yaml'
            else:
                destination = '/vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json'

            transfer_director_file_to_vm_vnfm(dir_connection, source, destination)

            log.info('waiting 2 seconds to transfer the file to VM-VNFM')
            time.sleep(2)
            log.info('nested connection close scale out')
            dir_connection.close()

        else:

            log.info('LCM Connection ')
            lcm_connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            sftp = lcm_connection.open_sftp()
            sftp.put(file_path + file_name, '/home/cloud-user/' + file_name)
            sftp.close()

            if node_name == 'TOSCA_DUMMY':
                command = ('sudo -i cp /home/cloud-user/vnflaf_cee-env.yaml '
                           '/vnflcm-ext/current/vnf_package_repo/vnflaf/HOT/Resources/EnvironmentFiles/'
                           'vnflaf_cee-env.yaml')
            else:
                command = ('sudo -i cp /home/cloud-user/VNFD_Wrapper_VNFLAF.json '
                           '/vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/'
                           'VNFD_Wrapper_VNFLAF.json')

            lcm_connection.exec_command(command, get_pty=True)
            time.sleep(2)
            lcm_connection.close()
            log.info('LCM Connection close')

        log.info('ECM connection open Scale out')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if 'TRUE' == is_vm_vnfm:
            evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)
            fetch_evnfm_instance_id(connection, evnfm_token, evnfm_hostname)
            log.info('Executing  curl command for ScaleOut of VNF with evnfm vnfinstance id: %s',
                     evnfm_vnf_instance_id)
        else:
            enm_token = Common_utilities.generate_enm_token(Common_utilities, connection, enm_hostname,
                                                            enm_username, enm_password)
            log.info('Start ScaleOut using ENM token: %s', enm_token)
            fetch_vnf_instance_id(connection, enm_token, enm_hostname, environment)
            log.info('Executing  curl command for ScaleOut of VNF with vnfinstance id: %s' + vnf_instance_id)

        if node_name == 'TOSCA_DUMMY':
            file_name = r'dummytoscascaleOutValues.json'
        else:
            file_name = r'scaleOutValues.json'

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        if 'TRUE' == is_vm_vnfm:
            curl = '''curl --insecure -H 'cookie: JSESSIONID={}' -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/scale{}'''.format(
                evnfm_token, file_name, evnfm_hostname, evnfm_vnf_instance_id, "'")
        else:
            curl = '''curl -k --cookie "iPlanetDirectoryPro={}" -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/scale{}'''.format(
                enm_token, file_name, enm_hostname, vnf_instance_id, "'")

        command = curl.replace('\n', '')
        log.info(command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('waiting for 60 seconds to kick off SCALE-OUT order')
        time.sleep(60)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        if 'TRUE' == is_vm_vnfm:
            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DSCALE%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vm_vnfm_name, vm_vnfm_manager_id, dummy_package_name, "'")

        else:
            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DSCALE%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vnf_manager_name, vnf_manager_id, onboard_package_name, "'")

        order_status, order_output = Common_utilities.scale_healorderReqStatus(Common_utilities, connection,
                                                                               curl, 30, 'SCALE-OUT')

        if order_status:
            log.info(' Order status of SCALE-OUT usecase is completed')
        else:
            log.info('Order Status of curl command for SCALE-OUT is failed with message:')
            log.info(order_output)
            connection.close()
            assert False

        log.info('waiting 120 seconds to scale out VM to come up')
        time.sleep(120)

        cmd = 'ping -w 3 ' + external_ip_for_services_vm_scale
        stdin, stdout, stderr = connection.exec_command(cmd)
        cmd_output = str(stdout.read())
        cmd_error = str(stderr.read())

        data_loss = ' 100% packet loss'

        if cmd_output.find(data_loss) == -1:
            log.info('Ping towards Scaled out VM is successful and Scaleout is Successful %s', cmd_output)
            connection.close()
        else:
            log.info('Ping towards Scaled out VM is Failed and ScaleOut has failed %s', cmd_output)
            connection.close()

    except Exception as e:
        log.error('Error During ScaleOut %s', str(e))
        assert False


def start_scale_in(node_name=''):
    log.info('Start SCALE-IN ')
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
        external_ip_for_services_vm_scale = sit_data._SIT__externalIpForServicesVmToScale
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        enm_hostname, enm_username, enm_password = Server_details.enm_host_server_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
        vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(
            Server_details)
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        if node_name == 'TOSCA_DUMMY':
            file_name = r'vnflaf_cee-env.yaml'
            file_path = 'com_ericsson_do_auto_integration_files/vnflaf/Resources/EnvironmentFiles/'
            servicesImage, tosca_dummy_depl_flavor = get_flavor_name_and_vimobjectId()
            update_vnflaf_yaml_scalefiles(file_path, file_name, servicesImage, tosca_dummy_depl_flavor,
                                          'Scale-In')
        else:
            file_name = r'VNFD_Wrapper_VNFLAF.json'
            file_path = 'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/'
            update_VNFD_wrapper_SCALE_IN(file_name)

        if 'TRUE' == is_vm_vnfm:
            log.info('nested connection open scale in')
            dir_connection = get_VMVNFM_host_connection()
            source_filepath = file_path + file_name
            ServerConnection.put_file_sftp(dir_connection, source_filepath,
                                           r'/home/' + vm_vnfm_director_username + '/' + file_name)
            source = '/home/{}/{}'.format(vm_vnfm_director_username, file_name)

            if node_name == 'TOSCA_DUMMY':
                destination = '/vnflcm-ext/current/vnf_package_repo/vnflaf/HOT/Resources/EnvironmentFiles/vnflaf_cee-env.yaml'
            else:
                destination = '/vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json'

            transfer_director_file_to_vm_vnfm(dir_connection, source, destination)

            log.info('waiting 2 seconds to transfer the file to VM-VNFM ')
            time.sleep(2)
            log.info('nested connection close scale in')
            dir_connection.close()

        else:
            lcm_connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            sftp = lcm_connection.open_sftp()
            sftp.put(file_path + file_name, '/home/cloud-user/' + file_name)
            sftp.close()
            if node_name == 'TOSCA_DUMMY':
                command = 'sudo -i cp /home/cloud-user/' + file_name + ' /vnflcm-ext/current/vnf_package_repo/vnflaf/HOT/Resources/EnvironmentFiles/vnflaf_cee-env.yaml'
            else:
                command = 'sudo -i cp /home/cloud-user/VNFD_Wrapper_VNFLAF.json /vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json'

            lcm_connection.exec_command(command, get_pty=True)
            time.sleep(2)
            lcm_connection.close()

        log.info('ECM connection open for scale in')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if 'TRUE' == is_vm_vnfm:
            evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)
            log.info('Executing  curl command for ScaleIn of VNF with evnfm vnfinstance id: %s', evnfm_vnf_instance_id)
        else:
            enm_token = Common_utilities.generate_enm_token(Common_utilities, connection, enm_hostname,
                                                            enm_username, enm_password)
            log.info('Start Scale in using ENM token: %s', enm_token)
            log.info('Executing  curl command for ScaleIn of VNF with vnfinstance id: %s', vnf_instance_id)

        if node_name == 'TOSCA_DUMMY':
            file_name = r'dummytoscascaleInValues.json'
        else:
            file_name = r'scaleInValues.json'

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        if 'TRUE' == is_vm_vnfm:
            curl = '''curl --insecure -H 'cookie: JSESSIONID={}' -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/scale{}'''.format(
                evnfm_token, file_name, evnfm_hostname, evnfm_vnf_instance_id, "'")

        else:
            curl = '''curl -k --cookie "iPlanetDirectoryPro={}" -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/scale{}'''.format(
                enm_token, file_name, enm_hostname, vnf_instance_id, "'")

        command = curl.replace('\n', '')
        log.info(command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('Waiting for 60 seconds to kick off SCALE-IN order')
        time.sleep(60)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        if 'TRUE' == is_vm_vnfm:

            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DSCALE%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vm_vnfm_name, vm_vnfm_manager_id, dummy_package_name, "'")

        else:

            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DSCALE%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vnf_manager_name, vnf_manager_id, onboard_package_name, "'")

        order_status, order_output = Common_utilities.scale_healorderReqStatus(Common_utilities, connection,
                                                                               curl, 30, 'SCALE-IN')
        if order_status:
            log.info('Order status of SCALE-IN usecase is completed')
        else:
            log.info('Order Status of curl command for SCALE_IN is failed with message:')
            log.info('Order output: %s', order_output)
            connection.close()
            assert False

        log.info('waiting 30 seconds to scale IN VM for ping response')
        time.sleep(30)

        cmd = 'ping -w 3 ' + external_ip_for_services_vm_scale
        stdin, stdout, stderr = connection.exec_command(cmd)
        cmd_output = str(stdout.read())
        cmd_error = str(stderr.read())

        data_loss = ' 0% packet loss'

        if cmd_output.find(data_loss) != -1:
            log.info('Scale-IN failed %s', cmd_output)
            connection.close()
        else:
            log.info('Scale-IN is successful %s', cmd_output)
            connection.close()

    except Exception as e:
        log.error('Error During ScaleIn %s', str(e))
        assert False


def start_heal(node_name=''):
    connection = None
    try:
        log.info('Start HEAL ')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        external_ip_for_services_vm = sit_data._SIT__external_ip_for_services_vm
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        environment = Server_details.ecm_host_blade_env(Server_details)
        enm_hostname, enm_username, enm_password = Server_details.enm_host_server_details(Server_details)
        openstack_ip, username, password, openrc_filename = Server_details.openstack_host_server_details(
            Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(
            Server_details)
        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)

        log.info('Fetching the VM VIM object id before starting Heal')

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'openstack server list | grep VNFLAF-Services-0 | grep {}'.format(
            external_ip_for_services_vm)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        if not stdout:
            log.info('No instantiated VM found using command: %s', command)
            ShellHandler.__del__(ShellHandler)
            assert False
        else:
            log.info('instantiated VM exists in list command %s', command)
            for line in stdout:
                vnf_data = line.split('|')
                vnf_id_before_heal = vnf_data[1].strip()
                log.info('VM VIM object id before starting heal: %s', vnf_id_before_heal)

        log.info('Start updating VNFD_Wrapper_VNFLAF.json with heal data')

        if node_name == 'TOSCA_DUMMY':
            file_name = r'vnflaf_cee-env.yaml'
            file_path = 'com_ericsson_do_auto_integration_files/vnflaf/Resources/EnvironmentFiles/'
            servicesImage, tosca_dummy_depl_flavor = get_flavor_name_and_vimobjectId()
            update_vnflaf_yaml_scalefiles(file_path, file_name, servicesImage, tosca_dummy_depl_flavor,
                                          'heal')

        elif node_name == 'SO-DUMMY-HEAL':
            file_name = 'vnflafecm_cee-env.yaml'
            file_path = 'com_ericsson_do_auto_integration_files/'
            update_vnflaf_yaml_scalefiles(file_path, file_name, '', '', 'SO-DUUMY-SCALE', node_name)

        else:
            file_name = r'VNFD_Wrapper_VNFLAF.json'
            file_path = 'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/'
            update_VNFD_wrapper_HEAL(file_name)

        if 'TRUE' == is_vm_vnfm:

            log.info('VM VNFM is true')
            log.info('nested connection open scale in')
            dir_connection = get_VMVNFM_host_connection()
            source_filepath = file_path + file_name
            ServerConnection.put_file_sftp(dir_connection, source_filepath,
                                           r'/home/' + vm_vnfm_director_username + '/' + file_name)

            source = '/home/{}/{}'.format(vm_vnfm_director_username, file_name)

            if node_name == 'TOSCA_DUMMY':

                destination = '/vnflcm-ext/current/vnf_package_repo/vnflaf/HOT/Resources/EnvironmentFiles/vnflaf_cee-env.yaml'

            elif node_name == 'SO-DUMMY-HEAL':
                destination = '/vnflcm-ext/current/vnf_package_repo/vnflafecm/HOT/Resources/EnvironmentFiles/' + file_name

            else:
                destination = '/vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json'

            transfer_director_file_to_vm_vnfm(dir_connection, source, destination)

            log.info('Waiting 2 seconds to transfer the file to VM-VNFM')
            time.sleep(2)

            log.info('Nested connection close scale in')
            dir_connection.close()

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
            evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)
            fetch_evnfm_instance_id(connection, evnfm_token, evnfm_hostname)

        else:
            log.info('LCM Connection open')
            lcm_connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            sftp = lcm_connection.open_sftp()
            sftp.put(file_path + file_name,
                     '/home/cloud-user/' + file_name)
            sftp.close()
            if node_name == 'TOSCA_DUMMY':
                command = 'sudo -i cp /home/cloud-user/' + file_name + ' /vnflcm-ext/current/vnf_package_repo/vnflaf/HOT/Resources/EnvironmentFiles/vnflaf_cee-env.yaml'
            elif node_name == 'SOL_DUMMY':
                command = f'sudo -i cp /home/cloud-user/{file_name} /vnflcm-ext/current/vnf_package_repo/vnflafecm/HOT/Resources/EnvironmentFiles/{file_name}'
            else:
                command = 'sudo -i cp /home/cloud-user/VNFD_Wrapper_VNFLAF.json /vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json'
            lcm_connection.exec_command(command, get_pty=True)
            time.sleep(2)
            lcm_connection.close()
            log.info('LCM Connection close')

            log.info('ECM connection open')
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            enm_token = Common_utilities.generate_enm_token(Common_utilities, connection, enm_hostname,
                                                            enm_username,
                                                            enm_password)
            log.info('Start Heal using ENM token: %s', enm_token)

            fetch_vnf_instance_id(connection, enm_token, enm_hostname, environment)

        if node_name == 'TOSCA_DUMMY' or node_name == 'SO-DUMMY-HEAL':
            file_name = r'dummytoscahealValues.json'
        else:
            file_name = r'healValues.json'

        sftp = connection.open_sftp()
        sftp.put('com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)
        sftp.close()

        if 'TRUE' == is_vm_vnfm:
            log.info(' executing  curl command for EVNFM Heal of VNF with vnfinstance id: %s', evnfm_vnf_instance_id)
            command = '''curl --insecure -i -H 'cookie: JSESSIONID={}' -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/heal{}'''.format(
                evnfm_token, file_name, evnfm_hostname, evnfm_vnf_instance_id, "'")
            log.info('evnfm heal command: %s', command)

        else:
            log.info('Executing  curl command for Heal of VNF with vnfinstance id: %s', vnf_instance_id)
            curl = '''curl -k --cookie "iPlanetDirectoryPro={}" -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/heal{}'''.format(
                enm_token, file_name, enm_hostname, vnf_instance_id, "'")
            command = curl.replace('\n', '')
            log.info('Command: %s', command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('Waiting for 180 seconds to kick off HEAL order')
        time.sleep(180)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        if 'TRUE' == is_vm_vnfm:
            log.info('VM VNFM is true')
            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DHEAL%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vm_vnfm_name, vm_vnfm_manager_id, dummy_package_name, "'")

        else:

            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DHEAL%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vnf_manager_name, vnf_manager_id, onboard_package_name, "'")

        order_status, order_output = Common_utilities.scale_healorderReqStatus(Common_utilities, connection, curl, 30,
                                                                               'HEAL')
        connection.close()

        log.info('Making ECM connection again to avoid connection break issues.')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if order_status:
            log.info(' Order status of Heal usecase is completed')

            ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
            command = 'source {}'.format(openrc_filename)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            command = 'openstack server list | grep VNFLAF-Services-0 | grep {}'.format(
                external_ip_for_services_vm)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

            for line in stdout:
                vnf_data = line.split('|')
                vnf_id_after_heal = vnf_data[1].strip()
                log.info('VM VIM object id after heal: %s', vnf_id_after_heal)
                log.info('COMPARING VM VIM OBJECT ID Before Heal: %s      VM VIM OBJECT ID AFTER Heal %s ',
                         vnf_id_before_heal, vnf_id_after_heal)

                if vnf_id_before_heal == vnf_id_after_heal:
                    log.info('Heal is not successful as VM VIM object id '
                             'of VNFLAF-Services-0 before and after are same')

                    ShellHandler.__del__(ShellHandler)
                    assert False

                else:
                    log.info('Heal is successful as VM VIM object id of VNFLAF-Services-0 are different')
                    cmd = 'ping -w 3 ' + external_ip_for_services_vm
                    stdin, stdout, stderr = connection.exec_command(cmd)
                    cmd_output = str(stdout.read())
                    cmd_error = str(stderr.read())
                    data_loss = ' 0% packet loss'

                    if cmd_output.find(data_loss) != -1:
                        log.info('Ping towards Healed VM is successful and Heal is Successful %s', cmd_output)
                    else:
                        log.info(order_output)
                        log.info('Ping towards the healed VM failed: %s', cmd_output)

            log.info('checking ECM for heal - COMPARING VM VIM OBJECT ID on open stack and ECM after HEAL.')
            command = '''curl --insecure --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/vms/'''.format(
                token, core_vm_hostname)

            log.info('VMS list command %s', command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            log.info('VMS list curl output %s', command_output)

            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            output = ast.literal_eval(command_out)

            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:
                if 'data' in output:
                    vms_output = output['data']['vms']

                    for vms_data in vms_output:
                        id = vms_data['vimObjectId']
                        if vnf_id_after_heal == id:
                            log.info('VM VIM OBJECT ID on open stack and '
                                     'ECM after HEAL are same. Heal Success')
                            break
                    else:
                        log.error('VM VIM OBJECT ID not found on ECM. Heal Fail')
                        assert False
                else:
                    log.info('No Data in command output for VMS list on ECM')
                    assert False

            elif 'ERROR' in requestStatus:
                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for VMS List %s', command_error)
                assert False

        else:
            log.info('Order Status of curl command for Heal verification is failed with message:')
            log.info('Order output %s', order_output)
            assert False

    except Exception as e:
        log.error('Error During Heal %s', str(e))
        assert False

    finally:
        connection.close()


def eocm_dummy_scale_out(file_name, option=''):
    try:
        log.info('Start ScaleOut ')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        environment = Server_details.ecm_host_blade_env(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        external_ip_for_services_vm_scale = sit_data._SIT__externalIpForServicesVmToScale
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        log.info('ECM connection open')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        fetch_vapp_instance_id(connection, environment, option)

        log.info('Making ECM connection again as connection closed in above method.')

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        curl = '''cd {}; curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken: {}' --data @{} 'https://{}/ecm_service/vapps/{}/scale{}'''.format(
            SIT.get_base_folder(SIT), token, file_name, core_vm_hostname, vapp_id, "'")

        log.info('Scale out command: %s', curl)
        stdin, stdout, stderr = connection.exec_command(curl)
        command_output = str(stdout.read())
        log.info('Scale out command output: %s', command_output)

        command_out = command_output[2:-1:1]
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']
        else:
            command_error = output['status']
            log.error('Error executing curl command for orderReqStatus %s', command_error)
            assert False

        order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                     core_vm_hostname, order_id, 30)

        if order_status:
            log.info(' Order status of SCALE-OUT usecase is completed ')

        else:
            log.info('Order Status of curl command for SCALE-OUT is failed with message:')
            log.info(order_status)
            connection.close()
            assert False

        log.info('waiting 120 seconds to scale out VM to come up')
        time.sleep(120)

        cmd = 'ping -w 3 ' + external_ip_for_services_vm_scale
        stdin, stdout, stderr = connection.exec_command(cmd)
        cmd_output = str(stdout.read())
        cmd_error = str(stderr.read())

        data_loss = ' 100% packet loss'

        if cmd_output.find(data_loss) == -1:
            log.info('Ping towards Scaled out VM is successful and Scaleout is Successful %s', cmd_output)
            connection.close()
        else:
            log.info('Ping towards Scaled out VM is Failed and ScaleOut has failed: %s', cmd_output)
            connection.close()

    except Exception as e:
        log.error('Error During ScaleOut %s', str(e))
        assert False


def eocm_dummy_scale_in(file_name, option=''):
    try:
        log.info('Start ScaleIn ')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        external_ip_for_services_vm_scale = sit_data._SIT__externalIpForServicesVmToScale
        environment = Server_details.ecm_host_blade_env(Server_details)

        log.info('ECM connection open')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        fetch_vapp_instance_id(connection, environment, option)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken: {}' --data @{} 'https://{}/ecm_service/vapps/{}/scale{}'''.format(
            token, file_name, core_vm_hostname, vapp_id, "'")

        log.info('Scale in command %s', curl)
        stdin, stdout, stderr = connection.exec_command(curl)

        command_output = str(stdout.read())
        log.info('Scale in command output %s', command_output)

        command_out = command_output[2:-1:1]
        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:
            order_id = output['data']['order']['id']
        else:
            command_error = output['status']
            log.error('Error executing curl command for orderReqStatus %s', command_error)
            assert False

        order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                     core_vm_hostname, order_id, 30)

        if order_status:
            log.info(' Order status of SCALE-IN usecase is completed')
        else:
            log.info('Order Status of curl command for SCALE_IN is failed with message:')
            log.info(order_output)
            connection.close()
            assert False

        log.info('Waiting 30 seconds to scale IN VM for ping response')

        time.sleep(30)

        cmd = 'ping -w 3 ' + external_ip_for_services_vm_scale
        stdin, stdout, stderr = connection.exec_command(cmd)
        cmd_output = str(stdout.read())
        cmd_error = str(stderr.read())

        data_loss = ' 0% packet loss'

        if cmd_output.find(data_loss) != -1:

            log.info('Scale-IN failed %s', cmd_output)
            connection.close()
        else:
            log.info('Scale-IN is successful %s', cmd_output)
            connection.close()

    except Exception as e:
        log.error('Error During EOCM Dummy Scalein: %s', str(e))
        assert False


def verify_node_heal_workflow_version():
    log.info('Start to verify DUMMY NODE HEAL Workflow Version')
    attribute_name = 'ONBOARD_PACKAGE'
    node_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, attribute_name)
    verify_worklow_version(node_name)


def epg_scale_heal(file_name, vapp_name, node_name):
    connection = None
    try:
        log.info('Start EPG HEAL')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        enm_hostname, enm_username, enm_password = Server_details.enm_host_server_details(Server_details)
        openstack_ip, username, password, openrc_filename = Server_details.openstack_host_server_details(
            Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(
            Server_details)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        is_vm_vnfm = sit_data._SIT__is_vm_vnfm
        external_ip_for_services_vm = sit_data._SIT__external_ip_for_services_vm
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

        environment = Server_details.ecm_host_blade_env(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        log.info('Fetching the VM VIM object id before starting Heal')

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'openstack server list | grep {}'.format(vapp_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        if not stdout:
            log.info('No instantiated VM found using command: %s', command)
            ShellHandler.__del__(ShellHandler)
            assert False
        else:
            log.info('instantiated VM exists in list command: %s', command)

            for line in stdout:
                vnf_data = line.split('|')
                vnf_id_before_heal = vnf_data[1].strip()
                log.info('VM VIM object id before starting heal: %s', vnf_id_before_heal)

        ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
        command = 'source {}'.format(openrc_filename)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = "openstack server stop {}".format(vapp_name)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        print(stdout)

        if 'TRUE' == is_vm_vnfm:

            evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
            evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)
            fetch_evnfm_instance_id(connection, evnfm_token, evnfm_hostname, node_name)

            log.info('Executing  curl command for EVNFM Heal of VNF with vnfinstance id: %s',
                     evnfm_vnf_instance_id)

            command = '''curl --insecure -i -H 'cookie: JSESSIONID={}' -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/heal{}'''.format(
                evnfm_token, file_name, evnfm_hostname, evnfm_vnf_instance_id, "'")

            log.info('evnfm heal command: %s', command)

            if vm_vnfm_namespace == 'codeploy':
                private_key_file = 'id_rsa_tf.pem'
            else:
                private_key_file = 'eccd-2-3.pem'

            source_path = SIT.get_base_folder(SIT) + file_name
            username = Ecm_core.get_vm_vnfm_director_username(Ecm_core)
            destination_path = f'/home/{username}/{file_name}'

            vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(Server_details)
            ServerConnection.transfer_files_with_an_encrypted_pem_file(connection, private_key_file, source_path,
                                                                       username, vm_vnfm_director_ip, destination_path)

        else:
            enm_hostname, enm_username, enm_password = Server_details.enm_host_server_details(Server_details)
            enm_token = Common_utilities.generate_enm_token(Common_utilities, connection, enm_hostname, enm_username,
                                                            enm_password)
            log.info('Start Heal using ENM token: %s', enm_token)

            fetch_vnf_instance_id(connection, enm_token, enm_hostname, environment, node_name)
            log.info('Executing  curl command for Heal of VNF with vnfinstance id: %s', vnf_instance_id)

            curl = '''curl -k --cookie "iPlanetDirectoryPro={}" -H "Content-Type: application/json" -X POST --data @{} 'https://{}/vnflcm/v1/vnf_instances/{}/heal{}'''.format(
                enm_token, file_name, enm_hostname, vnf_instance_id, "'")
            command = curl.replace('\n', '')
            log.info('Curl command: %s', command)
        command = f'cd {SIT.get_base_folder(SIT)}; {command}'
        stdin, stdout, stderr = connection.exec_command(command)
        log.info('Waiting for 150 seconds to kick off HEAL order')
        time.sleep(150)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        if 'TRUE' == is_vm_vnfm:

            log.info('VM VNFM is true')
            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DHEAL%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vm_vnfm_name, vm_vnfm_manager_id, dummy_package_name, "'")

        else:

            curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DHEAL%7C{}%7C{}%7CVAPP%7C{}{}'''.format(
                token, core_vm_hostname, vnf_manager_name, vnf_manager_id, onboard_package_name, "'")

        order_status, order_output = Common_utilities.scale_healorderReqStatus(Common_utilities, connection, curl, 30,
                                                                               'HEAL')
        connection.close()

        log.info('Making ECM connection again to avoid connection break issues')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if order_status:
            log.info(' Order status of Heal usecase is completed')

            openstack_ip, username, password, openrc_filename = Server_details.openstack_host_server_details(
                Server_details)
            ShellHandler.__init__(ShellHandler, openstack_ip, username, password)
            command = 'source {}'.format(openrc_filename)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            command = 'openstack server list | grep {}'.format(vapp_name)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            command_output = str(stdout)

            log.info('Command output: %s', command_output)

            for line in stdout:
                vnf_data = line.split('|')
                vnf_id_after_heal = vnf_data[1].strip()
                state = vnf_data[3].strip()
                log.info('VM VIM object id after heal: %s', vnf_id_after_heal)
                log.info('COMPARING VM VIM OBJECT ID: Before Heal %s    VM VIM OBJECT ID: AFTER Heal %s',
                         vnf_id_before_heal, vnf_id_after_heal)

                if 'ACTIVE' == state:
                    if vnf_id_before_heal == vnf_id_after_heal:
                        log.info('Heal is not successful as VM VIM object id of before and after are same')

                        ShellHandler.__del__(ShellHandler)
                        assert False
                    else:
                        log.info('Heal is successful')
                else:
                    log.info('Heal is not successful. Heal state - %s', state)
                    assert False

            log.info('Checking ECM for heal for EPG - COMPARING VM VIM '
                     'OBJECT ID on open stack and ECM after HEAL.')

            command = '''curl --insecure --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/vms/'''.format(
                token, core_vm_hostname)
            log.info('VMS list command %s', command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            log.info('VMS list curl output for EPG %s', command_output)

            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            output = ast.literal_eval(command_out)
            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:

                if 'data' in output:
                    vms_output = output['data']['vms']

                    for vms_data in vms_output:
                        id = vms_data['vimObjectId']
                        if vnf_id_after_heal == id:
                            log.info('VM VIM OBJECT ID on open stack and ECM after HEAL are same for EPG. '
                                     'Heal Success')
                            break
                    else:
                        log.error('VM VIM OBJECT ID not found on ECM for EPG. Heal Fail')
                        assert False

                else:
                    log.info('No Data in command output for VMS list on ECM for EPG')
                    assert False

            elif 'ERROR' in requestStatus:
                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for VMS List for EPG: %s', command_error)
                assert False

        else:
            log.info('Order Status of curl command for Heal verification is failed with message below')
            log.info(order_output)
            assert False

    except Exception as e:
        log.error('Error During EPG Heal %s', str(e))
        assert False

    finally:
        connection.close()
