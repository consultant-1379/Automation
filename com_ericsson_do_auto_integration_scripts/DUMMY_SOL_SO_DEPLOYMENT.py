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
import random
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
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import *
from com_ericsson_do_auto_integration_scripts.TOSCA_BGF_ECM_DEPLOYMENT import *

from com_ericsson_do_auto_integration_utilities.SO_file_update import (update_sol_service_template,
                                                                       update_sol_dummy_network_service_file)


log = Logger.get_logger('SOL_DUMMY_SO_DEPLOYMENT.py')


# In this file many methods of sol bgf is reused as functionality is same

def sol_dummy_package_download_parameter():
    add_package_download_parameter('SOL_DUMMY')


def create_sol_dummy_flavours():
    create_tosca_flavours(version='sol_dummy', tosca_bgf_flavor='CM-sol005_flavor_dummy')


def upload_sol_dummy_vnfd():
    try:
        log.info('Start to upload SOL DUMMY VNFD')
        Report_file.add_line('Start to upload SOL DUMMY VNFD')
        package_path = '/var/tmp/deploySOLDUMMY'
        package_name = 'vnflaf_etsi_tosca_9mb_valid.zip'
        pkg_name = package_name.split('.zip')[0]
        name = Common_utilities.get_name_with_timestamp(Common_utilities, pkg_name)

        update_runtime_env_file('ONBOARD_PACKAGE', name)

        file_name = 'onboard_sol_dummy.json'
        # using same method of sol bgf as functionality is same
        update_onboard_sol_bgf_file(file_name, package_name, name)
        onboard_tosca_node_package(file_name, package_name, package_path, 'SOL005_DUMMY_VNFD')

    except Exception as e:
        log.error('Error While uploading SOL005 DUMMY VNFD ' + str(e))
        Report_file.add_line('Error while uploading SOL005 DUMMY VNFD ' + str(e))
        assert False


def verify_dummy_sol_package():
    log.info('start verifying the onboarded sol005 dummy package')
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
        log.info('Finished onboarding package for sol005 dummy')
        Report_file.add_line('Finished onboarding package for sol005 dummy ')
        connection.close()
    else:

        log.error(
            'Verification of package uploaded failed. Please check the status of provisioning and operationalState  ')
        log.error('provisioningStatus : ' + provisioningStatus + ' operationalState : ' + operationalState)
        Report_file.add_line('Verification of package uploaded failed. Please check the status of provisioning and operationalState')
        log.info('Failed verification of package upload Doing Clean up of sol005 dummy Package ' + vnf_packageId)
        delete_tosca_vnf_package(vnf_packageId)
        assert False


def search_transfer_sol_dummy_image():
    image_name = 'ECM_TOSCA_Image_EO_Staging_9mb'
    search_transfer_image(image_name)


def sol_dummy_nsd_package_details():
    pkgs_dir_path = '/var/tmp/deploySOLDUMMY'
    package = 'ns_vnflaf_etsi_tosca.zip'
    packageName = package.split('.zip')[0]
    json_filename = 'createToscaNsdPackage.json'
    return pkgs_dir_path, package, packageName, json_filename


def create_sol_dummy_nsd():
    try:
        log.info('Start to create SOL005 DUMMY NSD package')
        Report_file.add_line('Start to create SOL005 DUMMY NSD package')
        pkgs_dir_path, package, packageName, json_filename = sol_dummy_nsd_package_details()
        create_nsd_package(packageName, json_filename)

    except Exception as e:
        log.error('Error While creating SOL005 DUMMY NSD package ' + str(e))
        Report_file.add_line('Error while creating SOL005 DUMMY NSD package ' + str(e))
        assert False


def upload_sol_dummy_nsd_package():
    try:
        log.info('Start to upload SOL005 DUMMY NSD package')
        Report_file.add_line('Start to upload SOL005 DUMMY NSD package')
        # etsi_tosca_bgf_deployment = 'ETSI_TOSCA_DEPL'
        pkgs_dir_path, package, packageName, json_filename = sol_dummy_nsd_package_details()
        upload_nsd_package(pkgs_dir_path, package)

    except Exception as e:
        log.error('Error While uploading SOL005 DUMMY NSD package ' + str(e))
        Report_file.add_line('Error while uploading SOL005 DUMMY NSD package ' + str(e))
        assert False


####################################################################################################################

def onboard_sol_dummy_subsytems():
    global so_version
    so_version = fetch_so_version('Sol005_Dummy')
    onboard_enm_ecm_subsystems('Sol005_Dummy')


def onboard_sol_dummy_config_template():
    global nsparam_form_name, vnfparam_form_name

    ns_param_file = 'dummy_nsAdditionalParams.json'

    nsparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'dummynsAdditionalParams')

    vnf_param_file = 'dummy_vnfAdditionalParams.json'

    vnfparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'dummyvnfAdditionalParams')

    onboard_sol_config_template(nsparam_form_name, ns_param_file, vnfparam_form_name, vnf_param_file, fetch_so_version('Sol005_Dummy'), key_check=False)


def onboard_sol_dummy_service_template():
    st_file_name = 'vnflaf_service_template.csar'

    update_sol_service_template(st_file_name, nsparam_form_name, vnfparam_form_name, 'sol005_dummy')

    onboard_so_template(st_file_name, 'Sol005_Dummy', so_version)


def create_sol_dummy_network_service():
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
    onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_PACKAGE')

    if so_version >= version.parse('2.11.0-118'):
        file_name = 'create_Dummy_NetworkService_Sol005_serviceOrder.json'
        update_sol_dummy_network_service_file(file_name, external_network_id, nsd_id, onboard_package_name, so_version)
        payload = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/' + file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        create_network_service(payload, so_version)
    else:
        file_name = 'create_Dummy_NetworkService_Sol005.json'
        update_sol_dummy_network_service_file(file_name, external_network_id, nsd_id, onboard_package_name, so_version)

        ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        # using this method as below method has the new API curl command which is used for dummy as well.
        create_network_service(file_name, so_version)


def verify_sol_dummy_service_status():
    poll_status_so()
