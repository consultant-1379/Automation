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

import ast
import time

from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.SO_Runtime_Operations import (fetch_action_id,
                                                                              get_so_service_id)
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization import Initialization_script
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import fetch_external_management_id
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import (get_VMVNFM_host_connection,
                                                                         transfer_director_file_to_vm_vnfm)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import action_status_so
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import (tosca_scale_service_state_check,
                                                                             check_state_network_service)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import poll_status_so
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import transfer_scale_files, lcm_transfer_scale_files

log = Logger.get_logger('SO_TOSCA_EPG_SCALE.py')


def scale_operations(file_name, operation):
    connection = None
    try:
        log.info('Start SO Tosca EPG %s', operation)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        so_host_name = sit_data._SIT__so_host_name
        epg_tosca_software_path = sit_data._SIT__epgToscaSoftwarePath

        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        command = f'cp {epg_tosca_software_path}/{file_name} {SIT.get_base_folder(SIT)}'
        log.info('Executing copy command: %s', command)

        stdin, stdout, stderr = connection.exec_command(command)
        handle_stderr(stderr, log)
        connection.close()

        attribute_name = 'ONBOARD_EPG_TOSCA_PACKAGE'
        service_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, attribute_name)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        so_token = Common_utilities.generate_so_token(
            Common_utilities,
            connection,
            so_host_name,
            token_user,
            token_password,
            token_tenant)

        service_id = get_so_service_id(
            connection, service_name, so_token, so_host_name)

        # storing the id as it will be used in polling so service state
        sit_data._SIT__network_service_id = service_id

        log.info('Service id is %s', service_id)

        command = (
            f'''curl -k -X PATCH -H 'cookie: JSESSIONID={so_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d @{file_name} https://{so_host_name}/orchestration/v1/services/{service_id}''')

        log.info('Executing command: %s', command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        log.info('Command output: %s', command_out)
        log.info('Checking action state')
        output = ast.literal_eval(command_out)
        action_id = fetch_action_id(output)
        log.info('Action id: %s', action_id)

        timeout = 50

        log.info('Waiting 10 sec for service state to be in progress')
        time.sleep(10)

        action_status_so(connection, so_token, so_host_name, action_id)

        connection.close()
        operations = ['SCALE-IN', 'SCALE-OUT']
        if operation in operations:
            poll_scale_so_status()
        else:
            # it will check service status , using a new fresh connection
            poll_status_so()

    except Exception as e:
        log.error('Error in SO service %s: %s', operation, str(e))
        assert False
    finally:
        connection.close()


def poll_scale_so_status():
    tosca_scale_service_state_check()


def check_so_network_service_state(connection, so_token, so_host_name, service_id):
    log.info('Start to check SO network service state')
    command = (
        f'''curl --insecure -H 'Cookie: JSESSIONID="{so_token}"' 'https://{so_host_name}/orchestration/v1/services/{service_id}{"'"}''')
    state = check_state_network_service(connection, command)
    return state


def transfer_xml_file():
    try:
        is_vm_vnfm = SIT.get_is_vm_vnfm(SIT)
        if is_vm_vnfm == 'TRUE':
            transfer_scale_files(['vsfo-cp3.xml', 'vsfo-cp4.xml'], "EPG_TOSCA_SCALE_HEAL")
        else:
            lcm_transfer_scale_files(['vsfo-cp3.xml', 'vsfo-cp4.xml'], "EPG_TOSCA_SCALE_HEAL")
    except Exception as e:
        log.error('Error in SO Tosca EPG xml file transfer %s', str(e))
        assert False


def so_tosca_epg_scale_out():
    log.info('Start Tosca EPG Scale-Out')
    scale_file = 'scaleOut_vEPG.json'
    transfer_xml_file()
    scale_operations(scale_file, 'SCALE-OUT')


def so_tosca_epg_scale_in():
    log.info('Start Tosca EPG Scale-In')
    scale_file = 'scaleIn_vEPG.json'
    transfer_xml_file()
    scale_operations(scale_file, 'SCALE-IN')
