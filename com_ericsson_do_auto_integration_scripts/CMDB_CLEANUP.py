# pylint: disable=W0703
# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under  which the
# program(s) have been supplied.
#
# ********************************************************************
"""
Module used to clean up remaining vapps/ns in EOCM from CMDB
"""
import ast

from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DELETION import get_vapp_list_from_eocm
from com_ericsson_do_auto_integration_scripts.ECM_NODE_REDISCOVERY import delete_vapp_from_cmdb_ecm
from com_ericsson_do_auto_integration_scripts.ECM_SERVICE_TERMINATE import fetch_ns_instance_ids
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_vapp_cmdb_del_file

log = Logger.get_logger('CMDB_CLEANUP.py')


def execute_cmdb_delete(connection, curl, name):
    """
    common method to run curl command and verify
    """
    log.info("Start deleting entity with name %s from cmdb", name)
    command_out = ExecuteCurlCommand.get_json_output(connection, curl)
    output = ExecuteCurlCommand.get_sliced_command_output(command_out)
    output = ast.literal_eval(output)
    request_status = output['status']['reqStatus']

    if 'SUCCESS' in request_status:
        log.info('Successfully deleted entity with name from cmdb %s', name)

    else:
        log.error("Error in deleting %s from cmdb , please check logs", name)
        assert False


def cleanup_vapps_cmdb():
    """
    This method will list down existing vapps in cmdb and delete
    """
    ecm_connection = None
    try:
        log.info("Start deleting vapps from cmdb")
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        ecm_connection, token = Common_utilities.get_eocm_connection_token(Common_utilities)

        vapp_list = get_vapp_list_from_eocm(ecm_connection, token, core_vm_hostname, 'ALL')

        for vapp in vapp_list:
            file_name = "cmdb_vapp_delete.json"
            log.info("Going to delete vapp with name %s", vapp["name"])
            update_vapp_cmdb_del_file(file_name, vapp["name"])
            delete_vapp_from_cmdb_ecm(vapp["name"], file_name)

        log.info("Successfully deleted vapps from cmdb")
    except Exception as error:
        log.error('Error while deleting vapps from cmdb : %s', str(error))
        assert False
    finally:
        if ecm_connection:
            ecm_connection.close()


def cleanup_network_service_cmdb():
    """
    This method will list down existing network services in cmdb and delete
    """
    connection = None
    try:
        log.info("Start deleting network service from cmdb")
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        instance_id_dict = fetch_ns_instance_ids()

        if instance_id_dict:

            connection, token = Common_utilities.get_eocm_connection_token(Common_utilities)

            for ns_name, ns_id in instance_id_dict.items():
                log.info("Going to delete network service with name %s", ns_name)

                curl = f'curl --insecure -X DELETE ' \
                       f'"https://{core_vm_hostname}/ecm_service/cmdb/ns_instances/{ns_id}" ' \
                       f'-H "Accept: application/json" ' \
                       f'-H "Content-Type: application/json" ' \
                       f'-H "AuthToken:{token}"'
                execute_cmdb_delete(connection, curl, ns_name)

            log.info("Successfully deleted network service from cmdb")
        else:
            log.info("No network service found in EOCM")
    except Exception as error:
        log.error('Error while deleting network service from cmdb : %s', str(error))
        assert False
    finally:
        if connection:
            connection.close()
