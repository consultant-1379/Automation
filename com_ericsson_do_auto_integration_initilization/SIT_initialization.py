'''
Created on 18 Oct 2018

@author: emaidns
'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_model.Ecde import Ecde
from com_ericsson_do_auto_integration_model.wano import wano
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.file_utils import create_temp_dir
import json

log = Logger.get_logger('SIT_initialization.py')

vdc_id = ''
external_net_id = ''
vnf_manager_id = ''
vimzone_id = ''
vdc_name = ''
image_auth_url = ''
project_id = ''
epg_vapp_name = ''
tosca_epg_vapp_name = ''
project_system_id = ''
vfc_onboarded_ids_dict = {}
vfc_certified_ids_dict = {}
ecde_fqdn = ''


class SIT_initialization():
    model_objects = {}

    def get_model_objects(self, key):
        return self.model_objects[key]

    def get_json_list_objects(self, key):
        return self.json_list_objects[key]

    def create_base_folder(self, connection):
        """
        Method to create temp directory on blade server for each jenkins job
        path : /tmp/automation_base_folder -should be present on blade
        """
        command = "mktemp -d -p /tmp/automation_base_folder/"
        tmp_dir = create_temp_dir(connection, command).strip()
        SIT.set_base_folder(SIT, tmp_dir)

    def collect_runtime_data(self, environment, connection, dynamic_project, is_vm_vnfm):
        # create_base_folder - to create base temp folder at the begining of each job
        self.create_base_folder(self, connection)
        data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
        source = r'/root/' + 'run_time_' + environment + '.json'
        ServerConnection.get_file_sftp(connection, source, data_file)

        global project_id
        project_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CEE_TENANT_ID')

        global project_system_id
        project_system_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'PROJECT_ID')

        # this image_auth_url is only used in ECDE onboarding system creation for vnfm type
        global image_auth_url
        image_auth_url = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'IMAGE_AUTH_URL')
        global vdc_name
        vdc_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VDC_NAME')

        global vdc_id
        vdc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VDC_ID')
        global vimzone_id
        vimzone_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VIMZONE_ID')
        global external_net_id
        external_net_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'EXTERNAL_NET_ID')
        global subsystem_name
        subsystem_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'SUBSYSTEM_NAME')
        global vnf_manager_id
        if dynamic_project:
            vnf_manager_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                   'DYNAMIC_VNF_MANAGER_ID')
        else:
            if 'TRUE' == is_vm_vnfm:
                vnf_manager_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                       'VM_VNFM_MANAGER_ID')
            else:
                vnf_manager_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VNF_MANAGER_ID')

        global epg_vapp_name
        epg_vapp_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_EPG_PACKAGE')

        global tosca_epg_vapp_name
        tosca_epg_vapp_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                    'ONBOARD_EPG_TOSCA_PACKAGE')

        global epg_pacakge_id
        epg_pacakge_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'EPG_PACKAGE_ID')

        global mme_vapp_name
        mme_vapp_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_MME_PACKAGE')

        global mme_package_id
        mme_package_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'MME_PACKAGE_ID')

        global cnf_vnfm_id
        cnf_vnfm_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CNF_VNFM_ID')

        global dummy_package_name
        dummy_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_PACKAGE')

        global sync_proj_vdc_name
        sync_proj_vdc_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'SYNC_PROJ_VDC_NAME')

        global sync_proj_vdc_id
        sync_proj_vdc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'SYNC_PROJ_VDC_ID')

        global vnf_identifier_id
        vnf_identifier_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VNF_IDENTIFIER_ID')

        global ccrc_resource_id
        ccrc_resource_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CCRC_RESOURCE_ID')

        global ccrc_upgrade_vnfd_id
        ccrc_upgrade_vnfd_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                     'CCRC_UPGRADE_VNFD_ID')

        global ccrc_deploy_vnfd_id
        ccrc_deploy_vnfd_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CCRC_DEPLOY_VNFD_ID')

        global vfc_onboarded_ids_dict

        resource_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_RESOURCE_VFC_ID')
        vfc_onboarded_ids_dict['RESOURCE'] = resource_vfc_id
        network_service_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                       'ONBOARD_NETWORK_SERVICE_VFC_ID')
        vfc_onboarded_ids_dict['NETWORK_SERVICE'] = network_service_vfc_id
        network_function_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                        'ONBOARD_NETWORK_FUNCTION_VFC_ID')
        vfc_onboarded_ids_dict['NETWORK_FUNCTION'] = network_function_vfc_id
        epg_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_EPG_VFC_ID')
        vfc_onboarded_ids_dict['EPG'] = epg_vfc_id

        global vfc_certified_ids_dict

        certify_resource_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                        'CERTIFY_RESOURCE_VFC_ID')
        vfc_certified_ids_dict['CERTIFY_RESOURCE'] = certify_resource_vfc_id
        certify_network_service_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                               'CERTIFY_NETWORK_SERVICE_VFC_ID')
        vfc_certified_ids_dict['CERTIFY_NETWORK_SERVICE'] = certify_network_service_vfc_id
        certify_network_function_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                                'CERTIFY_NETWORK_FUNCTION_VFC_ID')
        vfc_certified_ids_dict['CERTIFY_NETWORK_FUNCTION'] = certify_network_function_vfc_id
        certify_epg_vfc_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CERTIFY_EPG_VFC_ID')
        vfc_certified_ids_dict['CERTIFY_EPG'] = certify_epg_vfc_id
        certify_vf_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CERTIFY_VF_ID')
        vfc_certified_ids_dict['CERTIFY_VF'] = certify_vf_id

        certify_service_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CERTIFY_SERVICE_ID')
        vfc_certified_ids_dict['CERTIFY_SERVICE'] = certify_service_id

        global uds_vf_unique_id
        uds_vf_unique_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'VF_UNIQUE_ID')

        global ns_composition_id
        ns_composition_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                  'UNIQUE_ID_FROM_ADDING_NS_TO_COMPOSITION')

        global epg_composition_id
        epg_composition_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                   'UNIQUE_ID_FROM_ADDING_EPG_TO_COMPOSITION')

        global capabilities_unique_id
        capabilities_unique_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                       'UDS_CAPABILITIES_UNIQUE_ID')

        global requirements_unique_id
        requirements_unique_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                       'UDS_REQUIREMENTS_UNIQUE_ID')

        global uds_service_unique_id
        uds_service_unique_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                      'UDS_SERVICE_UNIQUE_ID')

        global uds_vf_name
        uds_vf_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'UDS_VF_NAME')

        global cnf_ns_instance_id
        cnf_ns_instance_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'CNF_NS_INSTANCE_ID')

        global tosca_epg_ns_instance_id
        tosca_epg_ns_instance_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                         'TOSCA_EPG_NS_INSTANCE_ID')
        global tosca_epg_vapp
        tosca_epg_vapp = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                               'TOSCA_EPG_VAPP')

        global etsi_tosca_epg_vapp
        etsi_tosca_epg_vapp = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                    'ETSI_TOSCA_EPG_VAPP')

        global etsi_tepg_ns_instance_id
        etsi_tepg_ns_instance_id = Json_file_handler.get_json_attr_value(Json_file_handler, data_file,
                                                                         'ETSI_TEPG_NS_INSTANCE_ID')

    def store_servers_data(self, file_data, dynamic_project):

        Initialization_script.store_ecm_core_data(Initialization_script, file_data, dynamic_project)
        Initialization_script.store_vnfm_data(Initialization_script, file_data)
        environment = file_data['ENVIRONMENT']
        server_ip = file_data['ECM_Host_Blade_IP']
        user_name = file_data['ECM_Host_Blade_username']
        password = file_data['ECM_Host_Blade_Password']
        is_vm_vnfm = file_data['IS_VM_VNFM'].upper()
        connection = ServerConnection.get_connection(server_ip, user_name, password)
        self.collect_runtime_data(self, environment, connection, dynamic_project, is_vm_vnfm)
        connection.close()

    def store_sit_data(self, file_data, dynamic_project, vnf_type, reconcile):

        log.info('start to collect system integration test data ')

        SIT.set_name(SIT, "")
        SIT.set_vnf_type(SIT, vnf_type)
        SIT.set_epg_flavors(SIT, file_data["EPG_FLAVORS"])
        SIT.set_epg_image_names(SIT, file_data['EPG_IMAGE_NAMES'])
        SIT.set_epg_image_ids(SIT, file_data['EPG_IMAGE_IDS'])
        SIT.set_mme_flavors(SIT, file_data["MME_FLAVORS"])
        SIT.set_mme_image_names(SIT, file_data['MME_IMAGE_NAMES'])
        SIT.set_mme_image_ids(SIT, file_data['MME_IMAGE_IDS'])
        SIT.set_tenant_name(SIT, file_data["TENANT_NAME"])
        SIT.set_software_version(SIT, file_data["SOFTWARE_VERSION"])
        SIT.set_is_public(SIT, file_data["IS_PUBLIC"])
        SIT.set_vnf_software_version(SIT, file_data["VNF_SOFTWARE_VESRION"])
        SIT.set_helm_deployment_name(SIT, file_data["HELM_DEPLOYMENT_NAME"])

        # FOR LCM shutdowm VM test for latest dummy node workflow
        # SIT.set_services_image(SIT, file_data["SERVICES_IMAGE_ID"])

        SIT.set_services_image(SIT, file_data["SERVICES_IMAGE_NAME"])

        SIT.set_services_flavor(SIT, file_data["SERVICES_FLAVOR"])
        SIT.set_external_net_id(SIT, external_net_id)
        SIT.set_external_subnet_cidr(SIT, file_data["EXTERNAL_SUBNET_CIDR"])
        SIT.set_external_subnet_gateway(SIT, file_data["EXTERNAL_SUBNET_GATEWAY"])
        if dynamic_project:
            if reconcile:
                SIT.set_external_ip_for_services_vm(SIT, file_data['RECONCILE_IP_FOR_DUMMY_VM'])
            else:
                SIT.set_external_ip_for_services_vm(SIT, file_data['EXTERNAL_IP_FOR_SERVICES_VM_DYNAMIC'])
        else:
            if reconcile:
                SIT.set_external_ip_for_services_vm(SIT, file_data['RECONCILE_IP_FOR_DUMMY_VM'])
            else:
                SIT.set_external_ip_for_services_vm(SIT, file_data['EXTERNAL_IP_FOR_SERVICES_VM'])

        SIT.set_cloud_manager_type(SIT, file_data["CLOUD_TYPE"])
        SIT.set_log_verify_host_url(SIT, file_data["LOGGING_VERIFICATION_HOST_URL"])
        SIT.set_oss_type(SIT, file_data["OSS_TYPE"])
        SIT.set_oss_master_host_name(SIT, file_data["OSS_MASTER_HOSTNAME"])
        SIT.set_oss_master_host_ip(SIT, file_data["OSS_MASTER_HOST_IP"])
        SIT.set_oss_notification_service_host(SIT, file_data["OSS_NOTIFICATION_SERVICE_HOST"])
        SIT.set_oss_notification_service_ip(SIT, file_data["OSS_NOTIFICATION_SERVICE_IP"])
        SIT.set_vnf_managers(SIT, vnf_manager_id)
        SIT.set_is_vm_vnfm(SIT, file_data["IS_VM_VNFM"])
        SIT.set_subsystem_name(SIT, subsystem_name)

        tenant_name = file_data['TENANT_NAME']

        if tenant_name == 'Sync_test':

            SIT.set_vdc_id(SIT, sync_proj_vdc_id)
            SIT.set_vdc_name(SIT, sync_proj_vdc_name)

        else:

            SIT.set_vdc_id(SIT, vdc_id)
            SIT.set_vdc_name(SIT, vdc_name)

        SIT.set_epg_vapp_name(SIT, epg_vapp_name)
        SIT.set_tosca_epg_vapp_name(SIT, tosca_epg_vapp_name)
        SIT.set_vnf_packageId(SIT, epg_pacakge_id)
        SIT.set_vimzone_id(SIT, vimzone_id)
        SIT.set_project_id(SIT, project_id)
        SIT.set_dummy_package_name(SIT, dummy_package_name)
        SIT.set_project_system_id(SIT, project_system_id)
        SIT.set_vimzone_name(SIT, file_data['VIM_NAME_FOR_CLOUD'])
        SIT.set_so_host_name(SIT, file_data['SO_HOSTNAME'])
        SIT.set_epg_software_path(SIT, file_data['EPG_SOFTWARE_PATH'])
        SIT.set_cnf_configmap_software_path(SIT, file_data['CNF_CONFIGMAP_SOFTWARE_PATH'])
        SIT.set_egad_cert_registery_name(SIT, file_data['EGAD_CERT_REGISTERY_NAME'])
        SIT.set_epg_tosca_software_path(SIT, file_data['EPG_TOSCA_SOFTWARE_PATH'])
        SIT.set_epg_tosca_flavors(SIT, file_data["EPG_TOSCA_FLAVORS"])
        SIT.set_epg_tosca_image_ids(SIT, file_data['EPG_TOSCA_IMAGE_IDS'])
        SIT.set_epg_tosca_image_names(SIT, file_data['EPG_TOSCA_IMAGE_NAMES'])
        SIT.set_epg_etsi_nsd_software_path(SIT, file_data['EPG_ETSI_NSD_PATH'])
        SIT.set_dcgw_software_path(SIT, file_data['DCGW_SOFTWARE_PATH'])
        SIT.set_enm_software_path(SIT, file_data['ENM_SOFTWARE_PATH'])
        SIT.set_epg_version(SIT, file_data['EPG_VERSION'])
        SIT.set_epg_etsi_nsd_version(SIT, file_data['EPG_ETSI_NSD_VERSION'])
        SIT.set_mme_software_path(SIT, file_data['MME_SOFTWARE_PATH'])
        SIT.set_mme_version(SIT, file_data['MME_VERSION'])
        SIT.set_external_ip_for_services_vm_to_scale(SIT, file_data['EXTERNAL_IP_FOR_SERVICES_VM_SCALE_OUT'])
        SIT.set_vcisco_gateway_ip(SIT, file_data['VCISCO_GATEWAY_IP'])
        SIT.set_vcisco_flavour_name(SIT, file_data['VCISCO_FLAVOUR_NAME'])
        SIT.set_valid9m_flavour_name(SIT, file_data['VALID9m_FLAVOUR_NAME'])
        SIT.set_vcisco_image_name(SIT, file_data['VCISCO_IMAGE_NAME'])
        SIT.set_valid9m_image_name(SIT, file_data['VALID9m_IMAGE_NAME'])
        SIT.set_vcisco_image_id(SIT, file_data['VCISCO_IMAGE_ID'])
        SIT.set_valid9m_image_id(SIT, file_data['VALID9m_IMAGE_ID'])
        SIT.set_environment_user_platform(SIT, file_data["ENVIRONMENT_USER_PLATFORM"])
        SIT.set_json_file_data(SIT, SIT.get_json_file_data(SIT))
        SIT.set_dummy_mme_path(SIT, file_data['DUMMY_MME_SOFTWARE_PATH'])
        SIT.set_bgf_tosca_ip(SIT, file_data['TOSCA_BGF_IP'])
        SIT.set_mme_package_name(SIT, mme_vapp_name)
        SIT.set_mme_packageId(SIT, mme_package_id)
        SIT.set_so_deployment_type(SIT, file_data['SO_DEPLOYMENT_TYPE'])
        SIT.set_enm_deployment_type(SIT, file_data['ENM_DEPLOYMENT_TYPE'])
        SIT.set_oss_user_name(SIT, file_data['OSS_USER_NAME'])
        SIT.set_vnf_identifier_id(SIT, vnf_identifier_id)
        SIT.set_ccrc_resource_id(SIT, ccrc_resource_id)
        SIT.set_cnf_vnfm_id(SIT, cnf_vnfm_id)
        SIT.set_so_entity_check_user(SIT, file_data['SO_ENTITY_CHECK_USER'])
        SIT.set_so_namespace(SIT, file_data['SO_NAMESPACE'])
        SIT.set_uds_hostname(SIT, file_data['UDS_HOSTNAME'])
        SIT.set_uds_username(SIT, file_data['UDS_USERNAME'])
        SIT.set_vfc_onboarded_ids_dict(SIT, vfc_onboarded_ids_dict)
        SIT.set_vfc_certified_ids_dict(SIT, vfc_certified_ids_dict)
        SIT.set_uds_service_unique_id(SIT, uds_service_unique_id)
        SIT.set_requirements_unique_id(SIT, requirements_unique_id)
        SIT.set_capabilities_unique_id(SIT, capabilities_unique_id)
        SIT.set_ns_composition_id(SIT, ns_composition_id)
        SIT.set_epg_composition_id(SIT, epg_composition_id)
        SIT.set_uds_vf_unique_id(SIT, uds_vf_unique_id)
        SIT.set_cluster_config_file(SIT, file_data['CLUSTER_CONFIG_NAME'])
        SIT.set_uds_vf_name(SIT, uds_vf_name)
        SIT.set_is_ccd(SIT, file_data['IS_CCD'])
        SIT.set_ccrc_ip_address(SIT, file_data['CCRC_IP_ADDRESS'])
        SIT.set_cnf_ns_instance_id(SIT, cnf_ns_instance_id)
        SIT.set_tosca_epg_ns_instance_id(SIT, tosca_epg_ns_instance_id)
        SIT.set_tosca_epg_vapp(SIT, tosca_epg_vapp)
        SIT.set_etsi_tosca_epg_vapp(SIT, etsi_tosca_epg_vapp)
        SIT.set_etsi_tepg_ns_instance_id(SIT, etsi_tepg_ns_instance_id)
        SIT.set_ccrc_upgrade_vnfd_id(SIT, ccrc_upgrade_vnfd_id)
        SIT.set_ccrc_deploy_vnfd_id(SIT, ccrc_deploy_vnfd_id)
        SIT.set_vmvnfm_pod_0(SIT, None)
        SIT.set_vmvnfm_pod_1(SIT, None)

        self.model_objects['SIT'] = SIT

        log.info('Finished to collect system integration test data ')

    def store_ecde_data(self, file_data, dynamic_project):

        log.info('start to collect ecde data ')

        Ecde.set_image_auth_url(Ecde, image_auth_url)
        Ecde.set_project_id(Ecde, project_id)
        Ecde.set_ecde_enm_ipaddress(Ecde, file_data['ECDE_ENM_IP'])
        Ecde.set_ecde_enm_username(Ecde, file_data['ECDE_ENM_USERNAME'])
        Ecde.set_ecde_enm_password(Ecde, file_data['ECDE_ENM_PASSWORD'])

        Ecde.set_ecde_admin_username(Ecde, file_data['ECDE_ADMIN_USERNAME'])
        Ecde.set_ecde_admin_password(Ecde, file_data['ECDE_ADMIN_PASSWORD'])
        Ecde.set_ecde_ecm_dummy_ip(Ecde, file_data['ECDE_ECM_DUMMY_VNF_IP'])
        Ecde.set_ecde_vnflcm_dummy_ip(Ecde, file_data['ECDE_VNFLCM_DUMMY_VNF_IP'])
        Ecde.set_ecde_ecm_3pp_ips(Ecde, file_data['ECDE_ECM_3PP_VNF_IPs'])
        Ecde.set_ecde_aat_ip(Ecde, file_data['ECDE_AAT_IP'])
        Ecde.set_ecde_aat_username(Ecde, file_data['ECDE_AAT_USERNAME'])
        Ecde.set_ecde_aat_password(Ecde, file_data['ECDE_AAT_PASSWORD'])

        Ecde.set_ecde_spinnaker_username(Ecde, file_data['ECDE_SPINNAKER_USERNAME'])
        Ecde.set_ecde_spinnaker_password(Ecde, file_data['ECDE_SPINNAKER_PASSWORD'])

        Ecde.set_ecde_fqdn(Ecde, file_data['ECDE_FQDN'])
        Ecde.set_ecde_keycloak_fqdn(Ecde, file_data['ECDE_KEYCLOAK_FQDN'])
        Ecde.set_ecde_spinnaker_hostname(Ecde, file_data['ECDE_SPINNAKER_HOSTNAME'])

        self.model_objects['Ecde'] = Ecde

        log.info('Finished to collect ecde data ')

    def store_wano_data(self, file_data):

        log.info('start to collect wano data')
        wano.set_wano_hostname(wano, file_data['WANO_HOSTNAME'])
        wano.set_wano_username(wano, file_data['WANO_USERNAME'])
        wano.set_wano_password(wano, file_data['WANO_PASSWORD'])
        wano.set_metrics_host_url(wano, file_data['METRICS_HOST_URL'])
        wano.set_metrics_value_pack(wano, file_data['METRICS_VALUE_PACK'])
        self.model_objects['wano'] = wano

        log.info('Finished to collect wano data')

    def initialize_user_input(self, user_input_file, dynamic_project=False, vnf_type='', reconcile=False):
        log.info('Start to collect User_Inputs')

        try:

            with open(user_input_file, 'r') as user_input:

                file_data = json.load(user_input)
                self.store_servers_data(self, file_data, dynamic_project)
                self.store_sit_data(self, file_data, dynamic_project, vnf_type, reconcile)
                # ECDE data removed from schema as part of
                # https://jira-oss.seli.wh.rnd.internal.ericsson.com/browse/SM-120531
                # self.store_ecde_data(self, file_data, dynamic_project)
                self.store_wano_data(self, file_data)

        except ValueError as v:
            log.error('please correct the file :' + user_input_file + ' \nERROR : ' + str(v))
            assert False

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + user_input_file)
            assert False
        except Exception as e:

            log.error('Error while updating user inputs ' + str(e))
            assert False

        log.info('Finished to collect User_Inputs')
