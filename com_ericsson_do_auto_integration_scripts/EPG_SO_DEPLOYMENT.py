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
from packaging import version
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_model.EPIS import EPIS
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import (
    update_onboard_file, onboard_epg_package, verify_epg_package)
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import (
    so_files_transfer, fetch_nsd_package, update_NSD_template, onboard_enm_ecm_subsystems,
    onboard_NSD_Template, fetch_service_modelId_uds_so_template, onboard_so_template,
    create_network_service, poll_status_so, fetch_so_version)
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import (
    check_so_deploy_attribute, check_so_day1_configure_status, check_lcm_workflow_status,
    node_ping_response, check_enm_node_sync, check_node_ecm_order_status, check_bulk_configuration)
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.SO_file_update import (
    update_epg_uds_so_network_service_file, update_epg_network_service_file)
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.CURL_UDS_SERVICE_TEMPLATE_CREATION import CurlUdsSTCreation as get_cmd

log = Logger.get_logger('EPG_SO_DEPLOYMENT.py')

service_template = ''
epg_so_version = ''


def update_node_onboard_file():
    update_onboard_file()


def onboard_node_epg_package():
    onboard_epg_package()


def verify_node_epg_package():
    verify_epg_package()


def epg_so_files_transfer():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_software_path = sit_data._SIT__epgSoftwarePath
    node_package_name = sit_data._SIT__name

    epg_so_version = fetch_so_version('EPG')
    so_files_transfer(epg_software_path, 'EPG', node_package_name, epg_so_version)


def fetch_ccd_version():
    openstack_ip, username, password, openrc_filename = \
        Server_details.openstack_host_server_details(Server_details)
    directory_server_ip, directory_server_username = \
        Server_details.vm_vnfm_director_details(Server_details)
    connection = ServerConnection.get_connection(openstack_ip, username, password)
    ServerConnection.get_file_sftp(connection, r'/root/env06Files/eccd150-director-key',
                                    r'eccd150-director-key')
    # we are reducing sleep time from 80 to 10 if any issue occurs try to make it 80 again
    log.info('waiting for 10sec to get director key file')
    time.sleep(10)

    file_path = 'eccd150-director-key'
    nested_conn = ServerConnection.get_nested_server_connection(connection, openstack_ip,
                                                                directory_server_ip, directory_server_username,
                                                                file_path)
    time.sleep(2)

    command = 'cat /etc/eccd/eccd_image_version.ini | grep -i IMAGE_RELEASE'

    log.info('command to fetch out CCD version %s', command)

    stdin, stdout, stderr = nested_conn.exec_command(command)

    ccd_version = stdout.read().decode("utf-8")
    log.info('CCD version: %s', ccd_version)

    nested_conn.close()
    connection.close()

    log.info('updating jenkins artifactory file with image version')

    with open(
            r'/proj/eiffel052_config_fem1s11/slaves/EO-STAGING-SLAVE-1/workspace/EO_STAGING_CCD_Artifactory/artifacts.properties',
            "w+") as f:
        f.write(ccd_version)


def fetch_node_nsd_package():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_software_path = sit_data._SIT__epgSoftwarePath
    global epg_so_version
    epg_so_version = fetch_so_version('EPG')

    global nsd_package
    global service_template
    nsd_package = 'epg-nsd-csar.csar'

    if epg_so_version <= version.parse('1.2.2083'):

        service_template = 'ST_EPG.yaml'

    elif epg_so_version >= version.parse('2.0.0-70'):

        service_template = 'ST_EPG_CATALOG_new.yaml'

    else:

        service_template = 'ST_EPG_CATALOG.yaml'

    fetch_nsd_package(epg_software_path, nsd_package, service_template, epg_so_version)


def update_node_nsd_template():
    if epg_so_version <= version.parse('2.0.0-69'):

        unzipped_nsd_package = 'epg-nsd-csar'
        zipped_nsd_package = 'epg-nsd-csar.zip'
        update_NSD_template(nsd_package, unzipped_nsd_package, zipped_nsd_package, 'EPG', epg_so_version)

    else:

        log.info('No need to update NS1.yaml in this version of SO %s', str(epg_so_version))


def onboard_node_subsytems():
    onboard_enm_ecm_subsystems('EPG')


def onboard_node_nsd_template():
    onboard_NSD_Template(nsd_package, service_template, 'EPG', epg_so_version)


def fetch_service_model_id_uds():
    fetch_service_modelId_uds_so_template('EPG')


def onboard_node_service_template():
    file_name = service_template
    onboard_so_template(file_name, 'EPG', epg_so_version)


def create_epg_uds_so_network_service():
    if epg_so_version >= version.parse('2.11.0-118'):
        file_name = 'create_epg_uds_so_NetworkService_serviceOrder.json'
        update_epg_uds_so_network_service_file(file_name, epg_so_version)
        payload = Json_file_handler.get_json_data(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        create_network_service(payload, epg_so_version)
    else:
        file_name = 'create_epg_uds_so_NetworkService.json'

        update_epg_uds_so_network_service_file(file_name, epg_so_version)
        create_network_service(file_name, epg_so_version)


def create_node_network_service():
    if epg_so_version >= version.parse('2.11.0-118'):

        file_name = 'create_epg_NetworkService_serviceOrder.json'
        update_epg_network_service_file(file_name, epg_so_version)
        payload = Json_file_handler.get_json_data(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/' + file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        create_network_service(payload, epg_so_version)

    else:
        file_name = 'create_epg_NetworkService_new.json'

        update_epg_network_service_file(file_name, epg_so_version)
        create_network_service(file_name, epg_so_version)


def check_epg_so_deploy_attribute():
    check_so_deploy_attribute(1800)


def check_epg_so_day1_configure_status():
    check_so_day1_configure_status()


def check_epg_lcm_workflow_status():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__name
    node_defination_name = 'Instantiate vEPG on OpenStack'
    check_lcm_workflow_status(node_package_name, node_defination_name)


def check_epg_tosca_lcm_workflow_status():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__name

    node_defination_name = 'Instantiate VNF'
    check_lcm_workflow_status(node_package_name, node_defination_name)


def check_epg_enm_sync_status():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__name
    check_enm_node_sync(node_package_name)


def check_epg_ip_ping_status():
    file_data = Json_file_handler.get_json_data(Json_file_handler,
                                                r'com_ericsson_do_auto_integration_files/VNFD_Wrapper_EPG.json')
    ip_address = file_data['instantiateVnfOpConfig']['vnfIpAddress']
    node_ping_response(ip_address)


def check_epg_ecm_order():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__name
    package_id = sit_data._SIT__vnf_packageId
    check_node_ecm_order_status(node_package_name, package_id)


def verify_node_service_status():
    poll_status_so()


def check_epg_bulk_configuration():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    node_package_name = sit_data._SIT__name
    command = 'cmedit get SubNetwork=vEPG,MeContext= ' + node_package_name + ',ManagedElement=' + node_package_name + ',system=1'
    check_bulk_configuration('EPG', 'es:location', command, epg_so_version)


def create_uds_so_tepg_network_service():
    try:
        log.info("Started TEPG network service creation")
        file_name = "create_uds_so_tepg_service.json"
        update_create_uds_so_tepg_service_file(file_name)
        payload_file = Json_file_handler.get_json_data(Json_file_handler,
                                                  r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        epg_so_version = fetch_so_version('TEPG')
        create_network_service(payload_file, epg_so_version)
        log.info("TEPG network service creation completed")
    except Exception as error:
        log.error("Failed to create TEPG network service: %s", str(error))
        assert False


def fetch_uds_service_template_id():
    log.info('Start to get service model id and invariant uuid')
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    so_host_name = SIT.get_so_host_name(SIT)
    token_user = 'staging-user'
    token_password = 'Testing12345!!'
    token_tenant = 'staging-tenant'
    distributed_st_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                            "DISTRIBUTED_SERVICE_NAME")
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    so_token = Common_utilities.generate_so_token(
        Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
    )
    command = get_cmd.get_so_service_template_id(so_host_name, so_token, distributed_st_name)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    log.info("command to get uds service template id: %s", command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    log.info("command output: %s", command_out)
    if "requestError" in command_out or not command_out:
        log.error('Failed to create uds service')
        assert False
    command_out_dict = ast.literal_eval(command_out)
    service_model_id = command_out_dict[0]["referenceId"]
    invariant_uuid = command_out_dict[0]["invariantUUID"]
    log.info("Fetched service_model_id and invariant_uuid: %s, %s", service_model_id, invariant_uuid)
    return service_model_id, invariant_uuid


def update_create_uds_so_tepg_service_file(file_name):
    try:
        log.info("Started to update file %s", file_name)
        file = r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name
        site_name = EPIS.get_site_name(EPIS)
        vimzone_name = SIT.get_vimzone_name(SIT)
        subsystem_name = SIT.get_subsystem_name(SIT)
        target_vdc = SIT.get_vdc_id(SIT)
        vnfm_id = SIT.get_vnf_managers(SIT)
        vdc_name = SIT.get_vdc_name(SIT)
        tenant_name = SIT.get_tenant_name(SIT)
        vnf_instance_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,
                                                                       "ONBOARD_EPG_TOSCA_PACKAGE")
        nsd_id = "40c5edb5-54a6-41e5-8155-cebce4ee0b96"
        subnet_id = SIT.get_sub_network_system_id(SIT) #subnetId
        connected_vn = SIT.get_external_network_system_id(SIT) #connectedvn
        service_model_id, invariant_uuid = fetch_uds_service_template_id()

        log.info("Start creating service order payload %s", file_name)
        data =  {'@type': 'ServiceOrder',
                 'category': '',
                 'description': '',
                 'serviceOrderItem': [{'@type': 'ServiceOrderItem',
                                       'action': 'add',
                                       'id': '1',
                                       'service': {'description': 'instantiate tepg',
                                                   'name': vnf_instance_name,
                                                   'serviceCharacteristic': [
                                                       {'name': 'subnetId', 'value': subnet_id},
                                                       {'name': 'vnfmId', 'value': vnfm_id},
                                                       {'name': 'targetVdc', 'value': target_vdc},
                                                       {'name': 'connectedVn', 'value': connected_vn},
                                                       {'name': 'geosite_name', 'value': site_name},
                                                       {'name': 'epg_name', 'value': vnf_instance_name},
                                                       {'name': 'subsystem_accessId', 'value': 'ECM_Sol005'},
                                                       {'name': 'nsdId', 'value': nsd_id},
                                                       {'name': 'subsystem_name', 'value': subsystem_name},
                                                       {'name': 'vimzone0_name', 'value': vimzone_name},
                                                       {'name': 'vdcName', 'value': vdc_name},
                                                       {'name': 'connectionName', 'value': tenant_name},
                                                       {'name': 'ns_name', 'value': 'tepg_sol005'},
                                                       {'name': 'resourceType', 'value': 'Resource'}],
                                                   'serviceSpecification': {'description': 'instantiate tepg',
                                                                            'id': invariant_uuid,
                                                                            'name': vnf_instance_name,
                                                                            'serviceModelId': service_model_id,
                                                                            'version': '1.0'},
                                                   'type': 'RFS'}}]}

        Json_file_handler.update_json_file(Json_file_handler, file, data)
        log.info("Updating of file %s completed", file_name)
    except Exception as error:
        log.error("Failed to update file %s: %s", file_name, str(error))
        assert False

