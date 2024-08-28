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
import time
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SO_Cleanup import *
from com_ericsson_do_auto_integration_utilities.SO_file_update import *
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
from packaging import version

log = Logger.get_logger('SOL_BGF_SO_DEPLOYMENT.py')


def onboard_sol_bgf_subsytems():
    global so_version
    so_version = fetch_so_version('Sol005_BGF')
    onboard_enm_ecm_subsystems('Sol005_BGF')


def onboard_sol_bgf_config_template():
    global nsparam_form_name, vbgfparam_form_name

    ns_param_file = 'nsAdditionalParams.json'

    nsparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'nsAdditionalParams')

    vbgf_param_file = 'vbgfAdditionalParams.json'

    vbgfparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'vbgfAdditionalParams')

    onboard_sol_config_template(nsparam_form_name, ns_param_file, vbgfparam_form_name, vbgf_param_file, fetch_so_version('Sol005_BGF'))


def onboard_sol_bgf_service_template():
    st_file_name = 'vBGF_ServiceTemplate_sol005.yaml'

    update_sol_service_template(st_file_name, nsparam_form_name, vbgfparam_form_name, 'sol005_vbgf')

    onboard_so_template(st_file_name, 'Sol005_BGF', so_version)


def create_sol_bgf_network_service():
    external_network_id, sub_network_id, external_network_system_id, sub_network_system_id = fetch_external_subnet_id()

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    nsd_id, nsd_name = fetch_nsd_details(ecm_connection, core_vm_hostname)

    if so_version >= version.parse('2.11.0-118'):
        file_name = 'create_vBGF_NetworkSevice_Sol005_serviceOrder.json'
        update_sol005_bgf_network_service_file(file_name, external_network_system_id, sub_network_system_id, nsd_id,
                                               so_version)
        payload = Json_file_handler.get_json_data(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        create_network_service(payload, so_version)
    else:
        file_name = 'create_vBGF_NetworkSevice_Sol005.json'

        update_sol005_bgf_network_service_file(file_name, external_network_system_id, sub_network_system_id, nsd_id,
                                               so_version)

        ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        create_network_service(file_name, so_version)


def verify_sol_bgf_service_status():
    poll_status_so()
