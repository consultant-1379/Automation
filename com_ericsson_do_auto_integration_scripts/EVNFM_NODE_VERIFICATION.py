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
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
import ast
import time
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand

log = Logger.get_logger('EVNFM_NODE_VERIFICATION.py')


def verify_ccrc_onboarding_state(connection, evnfm_token, wait_time):
    """
    Verify onboardingState of CCRC package
    @param connection:
    @param evnfm_token:
    @param wait_time:
    @return:
    """
    try:

        log.info('Verifying onboardingState of CCRC package')
        Report_file.add_line('Verifying onboardingState of CCRC package')

        time_out = 5400

        log.info('Time out for this task is %s seconds', str(time_out))

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
        resource_id = sit_data._SIT__ccrc_resource_id
        output = ''

        command = ('''curl --insecure \
                            -H 'cookie: JSESSIONID={}' \
                            https://{}/vnfm/onboarding/api/vnfpkgm/v1/vnf_packages/{}'''
                   .format(evnfm_token, evnfm_hostname, resource_id))

        Report_file.add_line('Verify command : ' + command)

        while time_out >= 0:


            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

            output = ast.literal_eval(command_out)

            onboarding_state = output['onboardingState']

            if 'ONBOARDED' in onboarding_state:

                vnfd_id = output['vnfdId']
                pkg_id = output['id']
                return True, vnfd_id, pkg_id

            elif 'UPLOADING' in onboarding_state:

                log.info('Oboarding State is UPLOADING ')
                log.info('Waiting %s seconds for completion of onboarding ', str(wait_time))
                time_out = time_out - wait_time
                time.sleep(wait_time)

            elif 'PROCESSING' in onboarding_state:

                log.info('OnboardingState is PROCESSING ')
                log.info('Waiting %s seconds for completion of onboarding ', str(wait_time))
                time_out = time_out - wait_time
                time.sleep(wait_time)

            else:
                log.info('Onboarding state is %s', onboarding_state)
                return False, output, None

        log.info('Onboarding status polling has timed out after 90 min. %s', str(output))
        Report_file.add_line('Onboarding status polling has timed out after 90 min ' + str(output))
        assert False

    except Exception as e:

        log.info('Error verifying CCRC package onboarding state %s', str(e))
        Report_file.add_line('Error verifying CCRC package onboarding state ' + str(e))
        assert False


def check_ccrc_node_opertaion_state(connection,command,vnf_identifier_id):
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    #command_out = command_output[2:-1:1]

    if 'Connection prematurely closed BEFORE response' in command_output:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)
        Report_file.add_line('Connecting to ecm server Again')

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username,
                                                     ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        command = ('''curl --insecure \
                            -X GET https://{}/vnflcm/v1/resources/{} \
                            -H 'cookie: JSESSIONID={}{}'''
                   .format(evnfm_hostname, vnf_identifier_id, evnfm_token, "'"))

        Report_file.add_line('verify operationState of ccrc node  command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    
    output = ast.literal_eval(command_out)
            
            
    operation_state = output["lcmOperationDetails"][0]["operationState"]
    return operation_state,output

    output = ast.literal_eval(command_out)

    operation_state = output["lcmOperationDetails"][0]["operationState"]
    return operation_state, output


def verify_ccrc_node_operation_state(wait_time, node_name, vnf_identifier_id):
    """
    Verify node operation state
    @param wait_time:
    @param node_name:
    @param vnf_identifier_id:
    @return:
    """
    connection = None
    try:

        log.info('Verifying node operation state for  %s', node_name)
        Report_file.add_line('Verifying node operation state for  ' + node_name)

        time_out = 3600

        log.info('Time out for this task is 3600 seconds ')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username,
                                                     ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        command = ('''curl --insecure \
                            -X GET https://{}/vnflcm/v1/resources/{} \
                            -H 'cookie: JSESSIONID={}{}'''
                   .format(evnfm_hostname, vnf_identifier_id, evnfm_token, "'"))

        Report_file.add_line('Verify operationState of ccrc node  command : ' + command)

        while time_out >= 0:

            operation_state, output = check_ccrc_node_opertaion_state(connection, command, vnf_identifier_id)

            if 'COMPLETED' in operation_state:
                log.info('Operation_state is COMPLETED ')
                return True

            elif 'UPLOADING' in operation_state:

                log.info('Operation_state is UPLOADING ')
                log.info('Waiting %s seconds for completion of UPLOADING ', str(wait_time))
                time_out = time_out - wait_time
                time.sleep(wait_time)

            elif 'PROCESSING' in operation_state or 'STARTING' in operation_state:

                log.info('Operation_state is %s ', operation_state)
                log.info('Waiting %s seconds for completion of %s', str(wait_time), operation_state)
                time_out = time_out - wait_time
                time.sleep(wait_time)

            else:
                log.info('Operation state is %s', operation_state)
                return False

        log.info('Node state polling is timed out after 60 minutes. %s', str(output))
        Report_file.add_line('Node state polling is timed out after 60 minutes. ' + str(output))
        return False

    except Exception as e:

        log.info('Error verifying ccrc node operation state: %s', str(e))
        Report_file.add_line('Error verifying ccrc node operation state ' + str(e))
        return False
    finally:
        connection.close()
