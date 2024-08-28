'''
Created on 06 Apr 2020

@author: zsyapra

'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_scripts.VNF_LCM_ENM import update_hosts_file, get_key_pair_file, fetch_httpd_ips
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities import file_utils

log = Logger.get_logger('ENM_LCM_INTEGRATION')


def get_lcm_server_details():
    try:

        lcm_service_data = Initialization_script.get_model_objects(Initialization_script, 'LCM_SERVICE')
        server_ip = lcm_service_data._LCM_service__lcm_service_ip
        username = lcm_service_data._LCM_service__lcm_user_name
        password = lcm_service_data._LCM_service__lcm_password

        return server_ip, username, password

    except Exception as e:
        log.error('Error while fetching lcm server details from DIT ' + str(e))
        Report_file.add_line('Error while fetchin lcm server details from DIT ' + str(e))
        assert False


def get_blade_server_details():
    try:

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
        return ecm_server_ip, ecm_username, ecm_password

    except Exception as e:
        log.error('Error while fetching blade server details from DIT ' + str(e))
        Report_file.add_line('Error while fetching blade server details from DIT ' + str(e))
        assert False


def enm_lcm_integration_for_extra_small_venm(enm_deployment_type):
    try:
        log.info('Starting Script : ENM LCM Integration of Extra_Small_vENM. ')
        Report_file.add_line('Starting Script : ENM LCM Integration of Extra_Small_vENM. ')

        ecm_server_ip, ecm_username, ecm_password = get_blade_server_details()
        server_ip, username, password = get_lcm_server_details()
        nested_conn = ServerConnection.make_nested_server_connection(ecm_server_ip, ecm_username, ecm_password,
                                                                     server_ip, username, password)
        command = 'consul members | grep gui'
        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = stdout.read()
        Report_file.add_line('Command :' + command)
        string_data = command_output.decode("utf-8")
        Report_file.add_line('Command Output :' + string_data)
        output = string_data.split()
        vnf_ip = output[1].split(':')[0]
        log.info('vnf-ip to update in hosts file - ' + vnf_ip)
        get_key_pair_file(server_ip, username, password)
        update_hosts_file(server_ip, username, password, enm_deployment_type, vnf_ip, nested_conn)
        nested_conn.close()


    except Exception as e:
        log.error('Error During ENM LCM integration of Extra_Small_vENM ' + str(e))
        Report_file.add_line('Error Durinfg ENM LCM Integration of Extra_Small_vENM ' + str(e))
        assert False


def enm_lcm_integration_for_feature_test_single():
    try:
        log.info('Starting script : ENM LCM Integration of Featute_Test_Single')
        Report_file.add_line('Starting script : ENM LCM Integration of Feature_Test_Single')
        lcm_service_data = Initialization_script.get_model_objects(Initialization_script, 'LCM_SERVICE')
        server_ip = lcm_service_data._LCM_service__lcm_service_ip
        username = lcm_service_data._LCM_service__lcm_user_name
        password = lcm_service_data._LCM_service__lcm_password
        get_key_pair_file(server_ip, username, password)
        fetch_httpd_ips(server_ip, username, password)
        update_hosts_file(server_ip, username, password)

    except Exception as e:
        log.error('Error During ENM LCM integration of Feature_Test_Single ' + str(e))
        Report_file.add_line('Error During ENM Integration of Feature_Test_Single ' + str(e))
        assert False


def enm_lcm_integration():
    try:
        log.info('ENM Integration if deployment type is Extra_Small_vENM or Feature_Test_Single. ')
        Report_file.add_line('ENM Integration if deployment type is Extra_Small_vENM or Feature_Test_Single. ')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        enm_deployment_type = sit_data._SIT__enm_deployment_type
        if enm_deployment_type == 'Extra_Small_vENM':
            enm_lcm_integration_for_extra_small_venm(enm_deployment_type)
        else:
            enm_lcm_integration_for_feature_test_single()


    except Exception as e:
        log.error('Error During ENM Integration ' + str(e))
        Report_file.add_line('Error During ENM Integration ' + str(e))
        assert False
