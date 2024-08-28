# pylint: disable=C0302,C0103,C0301,C0412,E0602,W0621,W0601,W0401,C0411,R0915,E0602,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612
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
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *
import random
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import *
from com_ericsson_do_auto_integration_scripts.TOSCA_BGF_ECM_DEPLOYMENT import *
# from com_ericsson_do_auto_integration_scripts.EPG_ETSI_TOSCA_NSD_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SO_file_update import (
    update_sol_service_template,
    update_etsi_tosca_network_service_file)

log = Logger.get_logger('EPG_ETSI_TOSCA_NSD_DEPLOYMENT.py')

# In this file many methods of sol bgf is reused as functionality is same

nsparam_form_name = ''
vnfparam_form_name = ''


def etsi_tosca_nsd_package_details():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    pkgs_dir_path = sit_data._SIT__epgEtsiNsdSoftwarePath
    package = 'NSD_ETN.csar'
    package_name = package.split('.csar')[0]
    json_filename = 'createToscaNsdPackage.json'
    return pkgs_dir_path, package, package_name, json_filename


def create_etsi_tosca_nsd_package():
    try:
        log.info('Start to create NSD package')
        Report_file.add_line('Start to create ETSI TOSCA NSD package')
        pkgs_dir_path, package, package_name, json_filename = etsi_tosca_nsd_package_details()
        create_nsd_package(package_name, json_filename)

    except Exception as e:
        log.error('Error While creating NSD package %s', str(e))
        Report_file.add_line('Error while creating ETSI TOSCA NSD package ' + str(e))
        assert False


def upload_etsi_tosca_nsd_package():
    try:
        log.info('Start to upload Sol005 NSD package')
        Report_file.add_line('Start to upload Sol005 NSD package')
        # etsi_tosca_bgf_deployment = 'ETSI_TOSCA_DEPL'
        pkgs_dir_path, package, packageName, json_filename = etsi_tosca_nsd_package_details()
        upload_nsd_package(pkgs_dir_path, package)

    except Exception as e:
        log.error('Error While uploading SOL005 NSD package %s', str(e))
        Report_file.add_line('Error while uploading SOL005 NSD package ' + str(e))
        assert False


def update_etsi_tosca_onboard_file():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_etsi_tosca_nsd_software_path = sit_data._SIT__epgEtsiNsdSoftwarePath
    epg_etsi_tosca_nsd_version = sit_data._SIT__epgEtsiNsdVersion
    generic_update_onboard_file(epg_etsi_tosca_nsd_software_path, epg_etsi_tosca_nsd_version)


def onboard_etsi_tosca_config_template():
    global nsparam_form_name, vnfparam_form_name

    ns_param_file = 'epgnsAdditionalParams.json'
    nsparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'epgnsAdditionalParams')

    vnf_param_file = 'epgAdditionalParams.json'
    vnfparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'epgAdditionalParams')

    onboard_sol_config_template(nsparam_form_name, ns_param_file, vnfparam_form_name, vnf_param_file,
                                fetch_so_version('Sol005_EPG'), key_check=False)


def epg_etsi_tosca_files_transfer():
    """
    Onboard day1ConfigEPG_Sol005.xml
    """
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__name
    epg_etsi_tosca_nsd_software_path = sit_data._SIT__epgEtsiNsdSoftwarePath
    global so_version
    so_version = fetch_so_version('Sol005_EPG')
    so_files_transfer(epg_etsi_tosca_nsd_software_path, 'Sol005_EPG', node_package_name, so_version)


def onboard_etsi_node_subsytems():
    onboard_enm_ecm_subsystems('Sol005_EPG')


def onboard_etsi_tosca_service_template():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    st_file_name = 'EPG_ServiceTemplate_sol005.csar'
    day1_template_name = sit_data._SIT__day1_template_name
    update_sol_service_template(st_file_name, nsparam_form_name, vnfparam_form_name, 'Sol005_EPG', day1_template_name)
    # onboard_enm_ecm_subsystems('Sol005_EPG')
    onboard_so_template(st_file_name, 'Sol005_EPG', so_version)


def create_etsi_tosca_network_service():
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    external_network_id, sub_network_id, external_network_system_id, sub_network_system_id = fetch_external_subnet_id()

    environment = ecm_host_data._Ecm_PI__ECM_Host_Name
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
    core_vm_hostname = ecm_host_data._Ecm_PI__core_vm_hostname
    ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    nsd_id, nsd_name = fetch_nsd_details(ecm_connection, core_vm_hostname)

    data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
    source = r'/root/' + 'run_time_' + environment + '.json'
    ServerConnection.get_file_sftp(ecm_connection, source, data_file)

    # todo if run in parallel we need to manage below attribute in teh runtime file
    onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_EPG_PACKAGE')
    update_runtime_env_file('ETSI_TOSCA_EPG_VAPP', onboard_package_name)
    if so_version >= version.parse('2.11.0-118'):
        file_name = 'EPG_Tosca_DeployService_sol005_serviceOrder.json'
        update_etsi_tosca_network_service_file(file_name, external_network_id, nsd_id, onboard_package_name, so_version)
        payload = Json_file_handler.get_json_data(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        create_network_service(payload, so_version)
    else:
        file_name = 'EPG_Tosca_DeployService_sol005.json'
        update_etsi_tosca_network_service_file(file_name, external_network_id, nsd_id, onboard_package_name, so_version)

        ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/'+file_name,
                                       SIT.get_base_folder(SIT)+file_name)
        # using this method as below method has the new API curl command which is used for dummy as well.
        create_network_service(file_name, so_version)


def check_sol_epg_bulk_configuration():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__name
    command = 'cmedit get SubNetwork=vEPG,MeContext= ' + node_package_name + ',ManagedElement=' + node_package_name + ',system=1'
    check_bulk_configuration('EPG', 'es:location', command, so_version)


def check_etsi_tosca_epg_ip_ping_status():
    """
    epgAdditionalParams.json - file we are downloading in repo as part of onboard_sol_config_template method
    to fetch the ip address of ETSI tosca epg node
    """
    vnf_param_file = 'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json'
    vnf_config = Json_file_handler.get_json_attr_value(Json_file_handler, vnf_param_file,  'instantiateVnfOpConfig')
    node_ping_response(vnf_config["vnfIpAddress"])
