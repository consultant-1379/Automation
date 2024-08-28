from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
import random
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from platform import node
import base64
from base64 import b64encode, b64decode

log = Logger.get_logger('RECONCILE_DUMMY_ECM_DEPLOYMENT.py')


def update_reconcile_hot_yaml():
    try:

        log.info('Start updating reconcile hot yaml file and env file ')
        Report_file.add_line('Start updating reconcile hot yaml file and env file ')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        flavour_name = sit_data._SIT__services_flavor
        file_name = r'com_ericsson_do_auto_integration_files/reconcile_vnflaf/reconcile_vnflaf_cee.yaml'
        update_flavour(file_name, flavour_name)

        file_name = r'com_ericsson_do_auto_integration_files/reconcile_vnflaf/Resources/HotFiles/vnflaf-services.yaml'
        update_flavour(file_name, flavour_name)

        update_vnflaf_yaml(
            file_name='com_ericsson_do_auto_integration_files/reconcile_vnflaf/Resources/EnvironmentFiles/vnflaf_cee-env.yaml')

        log.info('Finished updating reconcile hot yaml file and env file ')
        Report_file.add_line('Finished updating reconcile hot yaml file and env file ')


    except Exception as e:
        log.info('Error updating reconcile hot yaml file and env file  ' + str(e))
        Report_file.add_line('Error updating reconcile hot yaml file and env file  ' + str(e))
        assert False


def update_reconcile_vnfd_wrapper():
    try:
        update_VNFD_wrapper(
            file_name=r'com_ericsson_do_auto_integration_files/reconcile_vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json')
    except Exception as e:
        log.info('Error updating reconcile VNFD_wrapper file  ' + str(e))
        Report_file.add_line('Error updating reconcile VNFD_wrapper file  ' + str(e))
        assert False


def transfer_reconcile_vnflaf_package():
    try:
        log.info('start transfering reconcile-vnflaf package to VNF-LCM ')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm

        if 'TRUE' == is_vm_vnfm:

            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
            connection = get_VMVNFM_host_connection()

            ServerConnection.put_folder_scp(connection, r'com_ericsson_do_auto_integration_files/reconcile_vnflaf',
                                            r'/home/eccd/')

            source = '/home/eccd/reconcile_vnflaf'
            destination = '/vnflcm-ext/current/vnf_package_repo/'
            transfer_director_file_to_vm_vnfm(connection, source, destination)
            log.info('waiting 2 seconds to transfer the file to VM-VNFM ')
            time.sleep(2)

            destination = destination + 'reconcile_vnlaf'
            cmd = f"chmod 777 -R {destination}"
            command = get_vmvnfm_pod_cmd(cmd)
            log.info('Giving permission to reconcile_vnflaf ')
            Report_file.add_line('command : ' + command)
            stdin, stdout, stderr = connection.exec_command(command)

            source = '/vnflcm-ext/current/vnf_package_repo/reconcile_vnflaf/reconcile_vnflaf_cee.yaml'
            destination = '/home/eccd/reconcile_vnflaf/'
            get_file_from_vm_vnfm(connection, source, destination)
            log.info('waiting 2 seconds to transfer the file to director server')
            time.sleep(2)

            ServerConnection.get_file_sftp(connection, '/home/eccd/reconcile_vnflaf/reconcile_vnflaf_cee.yaml',
                                           r'com_ericsson_do_auto_integration_files/reconcile_vnflaf_cee.yaml')


        else:

            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            ServerConnection.put_folder_scp(connection, r'com_ericsson_do_auto_integration_files/reconcile_vnflaf',
                                            '/vnflcm-ext/current/vnf_package_repo/')
            command = 'chmod 777 -R /vnflcm-ext/current/vnf_package_repo/reconcile_vnflaf'
            stdin, stdout, stderr = connection.exec_command(command)
            # To get the below  updated yaml file for checksum 
            ServerConnection.get_file_sftp(connection,
                                           '/vnflcm-ext/current/vnf_package_repo/reconcile_vnflaf/reconcile_vnflaf_cee.yaml',
                                           r'com_ericsson_do_auto_integration_files/reconcile_vnflaf_cee.yaml')

        log.info('Finished transfering reconcile-vnflaf package to VNF-LCM ')
    except Exception as e:
        log.info('Error transfering reconcile-vnflaf package to VNF-LCM ' + str(e))
        Report_file.add_line('Error transfering reconcile-vnflaf package to VNF-LCM ' + str(e))
        assert False
    finally:
        connection.close()


def update_reconcile_dummy_onboard_file():
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                    r'com_ericsson_do_auto_integration_files/reconcile_vnflaf/Resources/VnfdWrapperFiles/VNFD_Wrapper_VNFLAF.json')
        global package_name
        package_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'TEST_RECONCILE_DUMMY')
        sit_data._SIT__name = package_name
        log.info('RECONCILE DUMMY ONBOARD PACKAGE NAME ' + package_name)
        Report_file.add_line('RECONCILE DUMMY ONBOARD PACKAGE NAME  ' + package_name)
        onboard_file_name = 'reconcile_on_board.json'
        update_reconcile_onboard_file(r'com_ericsson_do_auto_integration_files/' + onboard_file_name, file_data,
                                      package_name)

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + onboard_file_name,
                                       SIT.get_base_folder(SIT) + onboard_file_name)
        ServerConnection.put_file_sftp(connection,
                                       r'com_ericsson_do_auto_integration_files/reconcile_vnflaf/reconcile_vnflaf_cee.yaml',
                                       SIT.get_base_folder(SIT) + 'reconcile_vnflaf_cee.yaml')

    except Exception as e:

        log.info('Error transfering reconcile-vnflaf package to VNF-LCM ' + str(e))
        Report_file.add_line('Error transfering reconcile-vnflaf package to VNF-LCM ' + str(e))
        assert False

    finally:

        connection.close()


def reconcile_onboard_dummy_package():
    upload_file = 'reconcile_vnflaf_cee.yaml'
    onboard_node_package('reconcile_on_board.json', upload_file, package_name)


def verify_reconcile_dummy_package():
    log.info('start verifying the reconcile onboarded dummy package')
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


def update_reconcile_dummy_deploy_file():
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

    file_name = 'reconcile_deploy.json'
    update_deploy_file(file_name='com_ericsson_do_auto_integration_files/reconcile_deploy.json')

    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                   SIT.get_base_folder(SIT) + file_name)

    connection.close()


def deploy_reconcile_dummy_package():
    deploy_node('reconcile_deploy.json')


def verify_reconcile_dummy_deployment():
    try:

        log.info('waiting 60 seconds to verification of node')
        time.sleep(60)
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

        provisioningStatus, operationalState = get_node_status(connection, token, core_vm_hostname, node_id)

        if 'ACTIVE' == provisioningStatus and 'INSTANTIATED' == operationalState:

            Report_file.add_line('provisioningStatus is : ' + provisioningStatus)
            Report_file.add_line('operationalState is : ' + operationalState)

            log.info('Verification of package deployment is success')
            Report_file.add_line('Verification of package deployment is successful')


        else:
            log.info(
                'Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response ')
            Report_file.add_line(
                'Verification of package deployment failed. Please check the status of provisioning and operationalState and ping response')

            assert False


    except Exception as e:

        log.error('Error verifying node deployment ' + str(e))
        Report_file.add_line('Error verifying node deployment ' + str(e))
        assert False
    finally:
        connection.close()
