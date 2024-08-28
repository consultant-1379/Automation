'''
Created on 15 Aug 2018

@author: emaidns
'''

import json
from com_ericsson_do_auto_integration_model.Atlas import Atlas
from com_ericsson_do_auto_integration_model.Vnfm import Vnfm
from com_ericsson_do_auto_integration_model.Nfvo import Nfvo
from com_ericsson_do_auto_integration_model.Cee import Cee
from com_ericsson_do_auto_integration_model.Ecm import Ecm
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.LCM_service import LCM_service
from com_ericsson_do_auto_integration_utilities import Integration_properties
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
import random

log = Logger.get_logger('Initialization_script.py')

CEE_Tenant_ID = ''
VDC_ID = ''


class Initialization_script():
    model_objects = {}

    def get_model_objects(self, key):
        return self.model_objects[key]

    def get_json_list_objects(self, key):
        return self.json_list_objects[key]

    def collect_runtime_data(self, environment, connection):

        data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
        source = r'/root/' + 'run_time_' + environment + '.json'
        ServerConnection.get_file_sftp(connection, source, data_file)
        global CEE_Tenant_ID
        CEE_Tenant_ID = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CEE_TENANT_ID')
        global VDC_ID
        VDC_ID = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VDC_ID')

    def store_ecm_core_data(self, file_data, dynamic_project=False):
        log.info('Going to collect ecm_core_data')
        lcm_deployment_type = file_data['LCM_DEPLOYMENT_TYPE']
        Ecm_core.set_enviornment(Ecm_core, file_data['ENVIRONMENT'])
        Ecm_core.set_ecm_host_blade_ip(Ecm_core, file_data['ECM_Host_Blade_IP'])
        Ecm_core.set_ecm_host_blade_username(Ecm_core, file_data['ECM_Host_Blade_username'])
        Ecm_core.set_ecm_host_blade_password(Ecm_core, file_data['ECM_Host_Blade_Password'])
        Ecm_core.set_core_vm_ip(Ecm_core, file_data['CORE_VM_APPLICATION_SERVICE_IP'])

        log.info('LCM deployment type is ' + lcm_deployment_type)

        if lcm_deployment_type == 'HA':
            Ecm_core.set_vnf_lcm_dynamic_servicedb_ip(Ecm_core, file_data['DYNAMIC_VNF_LCM_Service_VIP'])
            Ecm_core.set_vnf_lcm_dynamic_service_ip1(Ecm_core, file_data['DYNAMIC_VNF_LCM_Service_IP_1'])
            Ecm_core.set_vnf_lcm_dynamic_service_ip(Ecm_core, file_data['DYNAMIC_VNF_LCM_Service_IP'])
        else:
            Ecm_core.set_vnf_lcm_dynamic_servicedb_ip(Ecm_core, file_data['DYNAMIC_VNF_LCM_Service_IP'])

        if dynamic_project:
            if lcm_deployment_type == 'HA':

                Ecm_core.set_vnf_lcm_servicedb_ip(Ecm_core, file_data['DYNAMIC_VNF_LCM_Service_VIP'])
                Ecm_core.set_vnf_lcm_dynamic_service_ip1(Ecm_core, file_data['DYNAMIC_VNF_LCM_Service_IP_1'])
            else:
                Ecm_core.set_vnf_lcm_servicedb_ip(Ecm_core, file_data['DYNAMIC_VNF_LCM_Service_IP'])
        else:
            if lcm_deployment_type == 'HA':
                Ecm_core.set_vnf_lcm_servicedb_ip(Ecm_core, file_data['STATIC_VNF_LCM_Service_VIP'])

            else:
                Ecm_core.set_vnf_lcm_servicedb_ip(Ecm_core, file_data['STATIC_VNF_LCM_Service_IP'])

        Ecm_core.set_vnf_lcm_servicedb_username(Ecm_core, file_data['VNF_LCM_Service_Username'])
        Ecm_core.set_vnf_lcm_servicedb_password(Ecm_core, file_data['VNF_LCM_Service_Password'])
        Ecm_core.set_rpm_bundle_link(Ecm_core, file_data['RPM_BUNDLE_LINK'])
        Ecm_core.set_discovery_bundle_link(Ecm_core, file_data['DISCOVERY_BUNDLE_LINK'])
        Ecm_core.set_core_vm_hostname(Ecm_core, file_data['CORE_VM_Hostname'])
        Ecm_core.set_enm_hostname(Ecm_core, file_data['ENM_GUI_Hostname'])
        # MULTI_ENM_GUI_Hostname -- just to create second ENM subsystem in SO
        Ecm_core.set_multi_enm_hostname(Ecm_core, file_data['MULTI_ENM_GUI_Hostname'])
        Ecm_core.set_ecm_gui_username(Ecm_core, file_data['ECM_GUI_Username'])
        Ecm_core.set_ecm_gui_password(Ecm_core, file_data['ECM_GUI_Password'])
        Ecm_core.set_abcd_vm_ip(Ecm_core, file_data['ABCD_VM_IP'])
        Ecm_core.set_abcd_vm_username(Ecm_core, file_data['ABCD_VM_USERNAME'])
        Ecm_core.set_abcd_vm_password(Ecm_core, file_data['ABCD_VM_PASSWORD'])
        Ecm_core.set_evnfm_hostname(Ecm_core, file_data['EVNFM_HOSTNAME'])
        Ecm_core.set_evnfm_auth_username(Ecm_core, file_data['EVNFM_AUTH_USERNAME'])
        Ecm_core.set_evnfm_auth_password(Ecm_core, file_data['EVNFM_AUTH_PASSWORD'])
        Ecm_core.set_vm_vnfm_director_ip(Ecm_core, file_data['VM_VNFM_DIRECTOR_IP'])
        Ecm_core.set_cism_cluster_ip(Ecm_core, file_data['CISM_CLUSTER_IP'])
        Ecm_core.set_ccd1_vm_vnfm_director_ip(Ecm_core, file_data['CCD1_VM_VNFM_DIRECTOR_IP'])
        Ecm_core.set_ccd1_vm_vnfm_director_username(Ecm_core, file_data['CCD1_VM_VNFM_DIRECTOR_USERNAME'])
        Ecm_core.set_vm_vnfm_director_username(Ecm_core, file_data['VM_VNFM_DIRECTOR_USERNAME'])
        Ecm_core.set_vm_vnfm_namespace(Ecm_core, file_data['VM_VNFM_NAMESPACE'])
        Ecm_core.set_cism_register_url(Ecm_core, file_data['CISM_REGISTER_URL'])
        is_cloudnative = True if file_data['IS_CLOUDNATIVE'].strip().lower() == 'true' else False
        Ecm_core.set_is_cloudnative(Ecm_core, is_cloudnative)
        Ecm_core.set_ecm_certificate_path(Ecm_core, file_data['ECM_CERTIFICATE_PATH'])
        Ecm_core.set_ecm_certificate_bkp_path(Ecm_core, file_data['ECM_CERTIFICATE_BKP_PATH'])
        Ecm_core.set_ecm_namespace(Ecm_core, file_data['ECM_NAMESPACE'])
        self.model_objects['ECM_CORE'] = Ecm_core
        log.info('Finished to collect ecm_core_data')

    def store_atlas_data(self, file_data):
        # If we want to automate some user inputs then we can write in these methods.
        log.info('Going to collect atlas_data')
        cloud_type = file_data['CLOUD_TYPE']
        atlas_name = cloud_type + str(random.randint(0, 999))
        project_name = file_data['PROJECT_NAME'].strip()
        username = project_name + '_admin'
        password = project_name.capitalize() + '.laf'
        Atlas.set_name(Atlas, atlas_name)
        Atlas.set_type(Atlas, cloud_type)
        Atlas.set_default_vim(Atlas, Integration_properties.atlas_dafaultVim)
        Atlas.set_host_ip_address(Atlas, file_data['ATLAS_IP'])
        Atlas.set_host_name(Atlas, file_data['ATLAS_Hostname'])

        atlasAuth_url = 'https://' + file_data['ATLAS_Hostname'].strip() + ':443'
        Atlas.set_auth_url(Atlas, atlasAuth_url)

        tenants = [{'name': project_name, 'id': CEE_Tenant_ID, 'username': username,
                    'password': password,
                    'defaultTenant': Integration_properties.atlas_tenants_defaultTenant}]
        Atlas.set_tenants(Atlas, tenants)

        Atlas.set_json_file_data(Atlas, Atlas.get_json_file_data(Atlas))

        self.model_objects['ATLAS'] = Atlas

        log.info('Finished to collect atlas_data')

    def store_cee_data(self, file_data):

        log.info('Going to collect cee_data')
        project_name = file_data['PROJECT_NAME'].strip()
        key_stone = file_data['KEY_STONE']
        username = project_name + '_admin'
        password = project_name.capitalize() + '.laf'
        Cee.set_name(Cee, file_data['VIM_NAME_FOR_CLOUD'])
        Cee.set_type(Cee, file_data['CLOUD_TYPE'])
        Cee.set_default_vim(Cee, Integration_properties.cee_defaultVim)
        Cee.set_host_ip_address(Cee, file_data['CLOUD_Host_IP_Address'])
        Cee.set_host_name(Cee, file_data['CLOUD_Hostname'])
        Cee.set_auth_url(Cee, key_stone)
        if 'v3' in key_stone:

            tenants = [{"userDomain": "Default", "name": "Default", "id": "default", "username": username,
                        "password": password, "defaultTenant": "True",
                        "subTenants": [{"name": project_name, "id": CEE_Tenant_ID, "username": username,
                                        "password": password,
                                        "defaultSubTenant": Integration_properties.cee_tenants_defaultTenant}]}]

        else:
            tenants = [{'name': project_name, 'id': CEE_Tenant_ID, 'username': username,
                        'password': password,
                        'defaultTenant': Integration_properties.cee_tenants_defaultTenant}]

        Cee.set_tenants(Cee, tenants)

        Cee.set_json_file_data(Cee, Cee.get_json_file_data(Cee))

        self.model_objects['CEE'] = Cee
        log.info('Finished to collect cee_data')

    def store_ecm_data(self, file_data):
        log.info('Going to collect ecm_data')
        Ecm.set_name(Ecm, Integration_properties.ecm_name)
        Ecm.set_type(Ecm, Integration_properties.ecm_type)
        Ecm.set_default_vim(Ecm, Integration_properties.ecm_defaultVim)
        Ecm.set_host_ip_address(Ecm, file_data['CORE_VM_APPLICATION_SERVICE_IP'])
        Ecm.set_host_name(Ecm, file_data['CORE_VM_Hostname'])

        ecmAuth_url = 'https://' + file_data['CORE_VM_Hostname'].strip() + '/ecm_service/'
        Ecm.set_auth_url(Ecm, ecmAuth_url)

        tenant_name = file_data['TENANT_NAME']

        tenants = [{'name': tenant_name, 'id': Integration_properties.ecm_tenants_id,
                    'username': file_data['ECM_GUI_Username'].strip(),
                    'password': file_data['ECM_GUI_Password'].strip(),
                    'defaultTenant': Integration_properties.ecm_tenants_defaultTenant}]
        Ecm.set_tenants(Ecm, tenants)

        Ecm.set_json_file_data(Ecm, Ecm.get_json_file_data(Ecm))

        self.model_objects['ECM'] = Ecm
        log.info('Finished to collect ecm_data')

    def store_vnfm_data(self, file_data):
        log.info('Going to collect vnfm_data')
        Vnfm.set_name(Vnfm, 'VNFM_LCM_Info_Authentication')
        Vnfm.set_description(Vnfm, Integration_properties.registervnfm_description)
        Vnfm.set_type(Vnfm, Integration_properties.registervnfm_type)

        dit_sol_version = file_data['SOL_VERSION'].strip()

        if 'SOL241' == dit_sol_version:
            sol_version = 'v2.4.1'
        else:
            sol_version = 'v2.3.1'

        Vnfm.set_sol_version(Vnfm, sol_version)
        Vnfm.set_vendor(Vnfm, Integration_properties.registervnfm_vendor)
        site = file_data['SITE_NAME']
        Vnfm.set_siteName(Vnfm, site)
        Vnfm.set_vnfmType(Vnfm, Integration_properties.registervnfm_vnfmType)

        endpoints = [{'name': Integration_properties.registervnfm_endpoints_name,
                      'ipAddress': file_data['ENM_GUI_Hostname'].strip(),
                      'port': Integration_properties.registervnfm_endpoints_port,
                      'testUri': Integration_properties.registervnfm_endpoints_testUri}]
        Vnfm.set_endpoints(Vnfm, endpoints)

        default_Security_Config = {
            'securityType': Integration_properties.registervnfm_defaultSecurityConfig_securtiyType}
        Vnfm.set_defaultSecurityConfig(Vnfm, default_Security_Config)

        Vnfm.set_authIpAddress(Vnfm, file_data['ENM_GUI_Hostname'])
        Vnfm.set_enm_ipaddress(Vnfm, file_data['ENM_IP_ADDRESS'])
        Vnfm.set_authPort(Vnfm, Integration_properties.registervnfm_authPort)
        Vnfm.set_authPath(Vnfm, Integration_properties.registervnfm_authpath)
        Vnfm.set_authUserName(Vnfm, file_data['ENM_GUI_Username'])
        Vnfm.set_authPassword(Vnfm, file_data['ENM_GUI_Password'])
        Vnfm.set_authType(Vnfm, Integration_properties.registervnfm_authtype)

        Vnfm.set_json_file_data(Vnfm, Vnfm.get_json_file_data(Vnfm))

        self.model_objects['VNFM'] = Vnfm
        log.info('Finished to collect vnfm_data')

    def store_nfvo_data(self, file_data):
        log.info('Going to collect nfvo_data')
        Nfvo.set_isNfvoAvailable(Nfvo, Integration_properties.nfvoconfig_isNfoAvailable)
        Nfvo.set_isGrantSupported(Nfvo, Integration_properties.nfvoconfig_isGrantSupported)

        grant_url = 'http://' + file_data['CORE_VM_Hostname'].strip() + ':8080/ecm_service/grant/v1/grants'
        Nfvo.set_grantUrl(Nfvo, grant_url)

        Nfvo.set_username(Nfvo, file_data['ECM_GUI_Username'])
        Nfvo.set_password(Nfvo, file_data['ECM_GUI_Password'])

        Nfvo.set_core_vm_ip(Nfvo, file_data['CORE_VM_APPLICATION_SERVICE_IP'])
        Nfvo.set_core_vm_hostname(Nfvo, file_data['CORE_VM_Hostname'])

        Nfvo.set_subscriptionId(Nfvo, '')
        tenant_name = file_data['TENANT_NAME']
        Nfvo.set_tenantid(Nfvo, tenant_name)

        Nfvo.set_vdcId(Nfvo, VDC_ID)

        # base_url = 'https://' + file_data['CORE_VM_APPLICATION_SERVICE_IP'].strip() + ':443/ecm_service'

        base_url = 'https://' + file_data['CORE_VM_Hostname'].strip() + '/ecm_service'
        Nfvo.set_nfvoAuthUrl(Nfvo, base_url)

        enm_host_name = file_data['ENM_GUI_Hostname'].strip()
        Nfvo.set_enmHostName(Nfvo, enm_host_name)

        Nfvo.set_orvnfm_version(Nfvo, file_data['SOL_VERSION'].strip())

        Nfvo.set_json_file_data(Nfvo, Nfvo.get_json_file_data(Nfvo))

        self.model_objects['NFVO'] = Nfvo

        log.info('Finished to collect nfvo_data')

    def store_LCM_service_server_data(self, user_input_file):
        log.info('Going to collect LCM_service_server_data')
        try:
            with open(user_input_file, 'r') as user_input:
                file_data = json.load(user_input)
                lcm_deployment_type = file_data['LCM_DEPLOYMENT_TYPE']
                LCM_service.set_lcm_service_ip(LCM_service, file_data['LCM_SERVICE_IP'])
                LCM_service.set_lcm_user_name(LCM_service, file_data['LCM_USERNAME'])
                LCM_service.set_lcm_password(LCM_service, file_data['LCM_PASSWORD'])

                log.info('LCM deployment type is ' + lcm_deployment_type)

                if lcm_deployment_type == 'HA':

                    LCM_service.set_vnf_service_ip(LCM_service, file_data['STATIC_VNF_LCM_Service_VIP'])
                else:
                    LCM_service.set_vnf_service_ip(LCM_service, file_data['STATIC_VNF_LCM_Service_IP'])

                self.model_objects['LCM_SERVICE'] = LCM_service

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + user_input_file)
            assert False

        log.info('Finished to collect LCM_service_server_data')

    def store_user_input(self, user_input_file):
        log.info('Going to collect User_Inputs')
        components = ['VNFM', 'NFVO', 'CEE', 'ATLAS', 'ECM']

        try:

            with open(user_input_file, 'r') as user_input:

                file_data = json.load(user_input)

                self.store_ecm_core_data(self, file_data)
                environment = file_data['ENVIRONMENT']
                server_ip = file_data['ECM_Host_Blade_IP']
                user_name = file_data['ECM_Host_Blade_username']
                password = file_data['ECM_Host_Blade_Password']
                connection = ServerConnection.get_connection(server_ip, user_name, password)
                self.collect_runtime_data(self, environment.strip(), connection)
                connection.close()
                for component in components:
                    if component == 'ATLAS':
                        self.store_atlas_data(self, file_data)
                    elif component == 'CEE':
                        self.store_cee_data(self, file_data)
                    elif component == 'VNFM':
                        self.store_vnfm_data(self, file_data)
                    elif component == 'NFVO':
                        self.store_nfvo_data(self, file_data)
                    elif component == 'ECM':
                        self.store_ecm_data(self, file_data)
        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + user_input_file)
            assert False
        log.info('Finished to collect User_Inputs')
