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
'''
Created on May 17, 2021

@author: zsyapra
'''
import time
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.SO_file_update import (
    update_sol_cnf_configmap_st_template,
    update_sol_cnf_configma_netwrok_service_file
)
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *

log = Logger.get_logger('SO_CNF_CONFIGMAP_DEPL.py')


class CnfconfigmapDepl:

    def get_etsi_tosca_nsd_pkg_details(self):
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        pkgs_dir_path = sit_data._SIT__cnfconfigmapSoftwarePath
        package = 'nsd-002.zip'
        packageName = package.split('.zip')[0]
        json_filename = 'createToscaNsdPackage.json'
        return pkgs_dir_path, package, packageName, json_filename

    def create_cnfns_nsd_package(self):
        try:
            pkgs_dir_path, package, packageName, filename = self.get_etsi_tosca_nsd_pkg_details(self)
            create_nsd_package(packageName, filename)

        except Exception as e:
            log.error('Error While creating CNF NSD package ' + str(e))
            Report_file.add_line('Error while creating CNF NSD package ' + str(e))
            assert False

    def upload_etsi_tosca_nsd_pkg(self):
        try:

            pkgs_dir_path, package, packageName, filename = self.get_etsi_tosca_nsd_pkg_details(self)
            upload_nsd_package(pkgs_dir_path, package)

        except Exception as e:
            log.error('Error While uploading CNF NSD package ' + str(e))
            Report_file.add_line('Error while uploading CNF NSD package ' + str(e))
            assert False

    def upload_cnf_configmap_config_templates(self):

        global vnf1config_form_name, vnf2config_form_name, vnf1param_form_name, \
            vnf2param_form_name, cnfparam_form_name
        vnf1config_file = 'config_vnf01.cfg'
        vnf1config_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'config_vnf01')
        vnf2config_file = 'config_vnf02.xml'
        vnf2config_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'config_vnf02')
        vnf1param_file = 'vnf01AdditionalParams.json'
        vnf1param_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'vnf01AdditionalParams')
        vnf2param_file = 'vnf02AdditionalParams.json'
        vnf2param_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'vnf02AdditionalParams')
        cnfparam_file = 'cnfnsAdditionalParams.json'
        cnfparam_form_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'cnfnsAdditionalParams')
        files_dict = {vnf1config_file: vnf1config_form_name, vnf2config_file: vnf2config_form_name,
                      vnf1param_file: vnf1param_form_name, vnf2param_file: vnf2param_form_name,
                      cnfparam_file: cnfparam_form_name}
        onboard_cnf_sol_configmap_templates(fetch_so_version('SOL005_CONFIGMAP'), files_dict)


    def onboard_sol_cnf_subsytems(self):

        global so_version
        # Here using existing Subsystem
        so_version = fetch_so_version('SOL005_CONFIGMAP')
        onboard_enm_ecm_subsystems('SOL005_CONFIGMAP')

    def onboard_sol_bgf_service_template(self):

        file_name = 'ST_CNF_configmap.csar'

        update_sol_cnf_configmap_st_template(vnf1config_form_name, vnf2config_form_name, vnf1param_form_name,
            vnf2param_form_name, cnfparam_form_name, file_name)

        onboard_so_template(file_name, 'SOL005_EOCM', so_version, 'SOL-CNF-CONFIG-MAP')

    def create_sol_cnf_network_service(self):

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if so_version >= version.parse('2.11.0-118'):
            file_name = 'CNF_DeployService_serviceOrder.json'
            update_sol_cnf_configma_netwrok_service_file(file_name, so_version)
            payload = Json_file_handler.get_json_data(Json_file_handler,
                                                      r'com_ericsson_do_auto_integration_files/' + file_name)
            Report_file.add_line(' Passing Payload Data to Create Network Service ')
            create_network_service(payload, so_version)
        else:
            file_name = 'CNF_DeployService.json'
            update_sol_cnf_configma_netwrok_service_file(file_name, so_version)

            ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            create_network_service(file_name, so_version)

    def verify_cnf_so_network_service(self):
        poll_status_so()
