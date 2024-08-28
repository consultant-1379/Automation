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
import time
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SO_Cleanup import *
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *
from com_ericsson_do_auto_integration_utilities.SO_file_update import *
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
from packaging import version

log = Logger.get_logger('DUMMY_SO_DEPLOYMENT.py')

so_version = ''
st_file_name = ''


def update_dummy_nsd_template():
    global so_version
    so_version = fetch_so_version('Dummy')
    nsd_package = "NSD-Test-vEPG.csar"
    unzipped_nsd_package = "NSD-Test-vEPG"
    zipped_nsd_package = "NSD-Test-vEPG.zip"
    update_NSD_template(nsd_package, unzipped_nsd_package, zipped_nsd_package, 'Dummy', so_version)


def onboard_dummy_subsytems():
    onboard_enm_ecm_subsystems('Dummy')


def upload_ecm_dummy_template(st_file_name, so_version):
    try:
        ecm_file_name = 'EcmTemplateDummy.txt'
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_host_name = sit_data._SIT__so_host_name

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + ecm_file_name,
                                       SIT.get_base_folder(SIT) + ecm_file_name)

        so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                      token_password, token_tenant)
        global ecm_template_name

        ecm_template_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'Dummy' + '_ecm_template')

        curl = ExecuteCurlCommand.curl_onboard_so_template(so_version, ecm_file_name, ecm_template_name, so_host_name, so_token, 'CONFIG_TEMPLATE')

        command = curl
        log.info(command)
        Report_file.add_line('command :' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('command output :' + command_output)

        attribute_list2 = ['topology_template', 'node_templates', 'mmeTargetVnfNS', 'properties', 'SO_RESOURCE::customTemplates', 0]
        properties = [{'attr_list': attribute_list2, "attribute": 'catalogRef', "value": ecm_template_name}]
        Json_file_handler.update_st_package(Json_file_handler,
                                            r'com_ericsson_do_auto_integration_files/' + st_file_name, properties)

    except Exception as e:
        connection.close()
        log.error('Error uploading Dummy ECM template  ' + str(e))
        Report_file.add_line('Error uploading Dummy ECM template  ' + str(e))
        assert False


def onboard_dummy_nsd_template():
    global st_file_name

    if so_version <= version.parse('2.0.0-69'):
        st_file_name = 'ServiceTemplate_dummy.yml'
    else:
        log.info('SO version is' + str(so_version) + ' , Start uploading ECM template to SO ')

        st_file_name = 'New_ServiceTemplate_Dummy.csar'

        upload_ecm_dummy_template(st_file_name, so_version)

    onboard_NSD_Template('NSD-Test-vEPG.csar', st_file_name, 'Dummy', so_version)


def onboard_dummy_service_template():
    onboard_so_template(st_file_name, 'Dummy', so_version)


def create_dummy_network_service():
    if so_version >= version.parse('2.11.0-118'):
        file_name = 'createNetworkService_serviceOrder.json'
        update_network_service_file(file_name, so_version)
        payload = Json_file_handler.get_json_data(Json_file_handler,r'com_ericsson_do_auto_integration_files/'+ file_name)
        Report_file.add_line(' Passing Payload Data to Create Network Service ')
        create_network_service(payload, so_version)

    else:
        file_name = 'createNetworkService_new.json'
        update_network_service_file(file_name, so_version)
        create_network_service(file_name, so_version)


def verify_dummy_service_status():
    poll_status_so()


def verify_dummy_so_depl_workflow_version():
    attribute_name = 'ONBOARD_PACKAGE'
    node_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities, attribute_name)
    verify_worklow_version(node_name)
