'''
Created on 14 Jan 2021

@author: ehsmoad
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_utilities.Server_details import *


log = Logger.get_logger('L2_L3_DCGW.py')


def create_dcgw_eo_cm():
    try:
        log.info('Start Creating DC-GW in EO-CM')
        Report_file.add_line('Start Creating DC-GW in EO-CM')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        file_name = r'CREATE_DC_GW_EO_CM.json'
        update_l2_l3_dcgw_file(file_name)

        log.info('ECM connection open')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/'+file_name,
                                       SIT.get_base_folder(SIT)+file_name)

        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        Report_file.add_line(token)
        curl = '''curl --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/dcgws'''.format(
            token, file_name, core_vm_hostname)
        command = curl
        Report_file.add_line('DC-GW EO-CM creation curl  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('DC-GW EO-CM creation curl output' + command_output)
        Report_file.add_line('DC-GW EO-CM creation curl output' + command_output)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        global dc_gw_id

        if 'SUCCESS' in requestStatus:
            oderId = output['data']['order']['id']
            log.info('order_id : ' + oderId)
            Report_file.add_line('order_id : ' + oderId)
            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, oderId, 60)
            if order_status:
                log.info('Order Is Completed')
                log.info('Order Output' + str(order_output))
                log.info('Fetch DC-GW ID from order output')
                Report_file.add_line('Fetch DC-GW ID from order output')
                dc_gw_id = order_output['data']['order']['orderItems'][0]['registerDcgw']['id']
                # dc_gw_id = output['data']['order']['id']
                log.info('DC-GW ID from order output is ' + dc_gw_id)
                Report_file.add_line('DC-GW ID from order output is ' + dc_gw_id)



        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for Creataing L2-L3 DC-GW ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for Creataing L2-L3 DC-GW')
            connection.close()
            raise ValueError('Error executing curl command for Creataing L2-L3 DC-GW ')


    except Exception as e:
        log.error('ERROR ' + str(e))
        Report_file.add_line('Error  ' + str(e))
        assert False

    connection.close()
    log.info('L2-L3 DC-GW creation ends ')
    Report_file.add_line('L2-L3 DC-GW creation ends ')


def update_l2_l3_dcgw_file(filename):
    log.info('Start to update ' + filename)
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vimzone_id = sit_data._SIT__vimzone_id

    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    vcisco_management_ip = ecm_host_data._Ecm_PI__vCisco_Management_ip
    vcisco_management_username = ecm_host_data._Ecm_PI__vCisco_Management_username
    vcisco_management_password = ecm_host_data._Ecm_PI__vCisco_Management_Password

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    site_name = EPIS_data._EPIS__site_name

    file_name1 = 'com_ericsson_do_auto_integration_files/' + filename

    global dc_gw_name
    dc_gw_name = 'DC_GW_' + str(random.randint(0, 999))
    Json_file_handler.modify_attribute(Json_file_handler, file_name1, 'name', dc_gw_name)

    Json_file_handler.modify_attribute(Json_file_handler, file_name1, 'managementIpAddress', vcisco_management_ip)

    Json_file_handler.update_any_json_attr(Json_file_handler, file_name1, ['credentials'], 'username',
                                           vcisco_management_username)

    Json_file_handler.update_any_json_attr(Json_file_handler, file_name1,
                                           ['credentials'], 'password',
                                           vcisco_management_password)

    Json_file_handler.modify_attribute(Json_file_handler, file_name1, 'siteName', site_name)

    Json_file_handler.update_any_json_attr(Json_file_handler, file_name1,
                                           ['vimzones', 0], 'id',
                                           vimzone_id)

def verify_l2_l3_dcgw_creation():
    try:
        log.info('Verify DC-GW creation using DC-GW ID')
        Report_file.add_line('Verify DC-GW creation using DC-GW ID')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        log.info('ECM connection open')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        Report_file.add_line(token)
        curl = '''curl --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/dcgws/{}'''.format(
                token, core_vm_hostname, dc_gw_id)
        command = curl
        Report_file.add_line('Get DC-GW EO-CM curl  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('Get DC-GW EO-CM Verification curl output' + command_output)
        Report_file.add_line('Get DC-GW EO-CM Verification curl output' + command_output)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            connectivityStatus = output['data']['dcgw']['lastKnownConnectivityStatus']

            if 'DOWN' in connectivityStatus:

                log.error('DC-GW Connectivity status is : ' + connectivityStatus)
                Report_file.add_line('DC-GW Connectivity status is : ' + connectivityStatus)
                connection.close()
                assert False

            elif 'UP' in connectivityStatus:
                log.info('DC-GW Connectivity status is : ' + connectivityStatus)
                Report_file.add_line('DC-GW Connectivity status is : ' + connectivityStatus)
                connection.close()


        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for verification of L2-L3 DC-GW ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for verification of L2-L3 DC-GW')
            connection.close()
            raise ValueError('Error executing curl command for verification of L2-L3 DC-GW ')


    except Exception as e:
        log.error('ERROR ' + str(e))
        Report_file.add_line('Error  ' + str(e))
        assert False

    connection.close()
    log.info('L2-L3 DC-GW verification ends ')
    Report_file.add_line('L2-L3 DC-GW verification ends ')



def create_vrf_dcgw():
    try:
        log.info('Start Creating and check VRF in DC-GW')
        Report_file.add_line('Start Creating and check VRF in DC-GW')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        file_name = r'CREATE_VRF_EO_CM.json'
        update_create_vrf_file(file_name)

        log.info('ECM connection open')
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/'+file_name,
                                       SIT.get_base_folder(SIT)+file_name)

        log.info('Generating token in the host blade server using the  curl command  ')
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        Report_file.add_line(token)
        curl = '''curl --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @{} https://{}/ecm_service/dcgwvrfs'''.format(
            token, file_name, core_vm_hostname)
        command = curl
        Report_file.add_line('Create VRF DC-GW creation curl  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('Create VRF DC-GW curl output' + command_output)
        Report_file.add_line('Create VRF DC-GW curl output' + command_output)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']

        global dc_gw_id

        if 'SUCCESS' in requestStatus:
            oderId = output['data']['order']['id']
            log.info('order_id : ' + oderId)
            Report_file.add_line('order_id : ' + oderId)
            order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection, token,
                                                                         core_vm_hostname, oderId, 60)
            if order_status:
                log.info('Order Is Completed')
                log.info('Order Status Output' + str(order_output))
                Report_file.add_line('Order is completed. Order Status Output' + str(order_output))

            else:
                log.info(order_output)
                log.info('Order Status is failed with message mentioned above ' + oderId)
                Report_file.add_line('Order Status is failed with message mentioned above ' + oderId)
                connection.close()
                assert False

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for Creating VRF DC-GW ' + command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for Creating VRF DC-GW')
            connection.close()
            raise ValueError('Error executing curl command for Creating VRF DC-GW')


    except Exception as e:
        log.error('ERROR ' + str(e))
        Report_file.add_line('Error  ' + str(e))
        assert False

    connection.close()
    log.info('VRF creation / check in DC-GW ends ')
    Report_file.add_line('VRF creation / check in DC-GW ends ')


def update_create_vrf_file(filename):
    log.info('Start to update ' + filename)

    vrf_id_on_device = 'SCM-VRF-OM_CN_DEMO'
    vrf_name = 'VRF_' + str(random.randint(0, 999))

    file_name1 = 'com_ericsson_do_auto_integration_files/' + filename

    Json_file_handler.modify_attribute(Json_file_handler, file_name1, 'name', vrf_name)
    Json_file_handler.modify_attribute(Json_file_handler, file_name1, 'vrfIdOnDevice', vrf_id_on_device)

    Json_file_handler.update_any_json_attr(Json_file_handler, file_name1, ['dcgw'], 'id',
                                           dc_gw_id)

    Json_file_handler.update_any_json_attr(Json_file_handler, file_name1,
                                           ['dcgw'], 'name',
                                           dc_gw_name)

    log.info(filename + 'has been updated')
