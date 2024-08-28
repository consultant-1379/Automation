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
Created on 18 Oct 2018

@author: emaidns
'''

import random


class SIT(object):
    def get_invariant_uuid(self):
        return self.__invariant_uuid

    def set_invariant_uuid(self, value):
        self.__invariant_uuid = value

    def get_tosca_epg_vapp_name(self):
        return self.__tosca_epg_vapp_name

    def set_tosca_epg_vapp_name(self, value):
        self.__tosca_epg_vapp_name = value

    def get_epg_tosca_software_path(self):
        return self.__epgToscaSoftwarePath

    def set_epg_tosca_software_path(self, value):
        self.__epgToscaSoftwarePath = value

    def get_epg_tosca_image_names(self):
        return self.__epg_tosca_image_names

    def set_epg_tosca_image_names(self, value):
        self.__epg_tosca_image_names = value.strip()

    def get_epg_tosca_image_ids(self):
        return self.__epg_tosca_image_ids

    def set_epg_tosca_image_ids(self, value):
        self.__epg_tosca_image_ids = value.strip()

    def get_epg_tosca_flavors(self):
        return self.__epg_tosca_flavors

    def set_epg_tosca_flavors(self, value):
        self.__epg_tosca_flavors = value.strip()

    def set_cnf_configmap_software_path(self, value):
        self.__cnfconfigmapSoftwarePath = value

    def get_cnf_configmap_software_path(self):
        return self.__cnfconfigmapSoftwarePath

    def set_egad_cert_registery_name(self, Value):
        self.__egadcert_registery_name = Value

    def get_egad_cert_registery_name(self):
        return self.__egadcert_registery_name

    def get_cluster_config_file(self):
        return self.__cluster_config_file

    def set_cluster_config_file(self, value):
        self.__cluster_config_file = value

    def get_day1_template_name(self):
        return self.__day1_template_name

    def set_day1_template_name(self, value):
        self.__day1_template_name = value

    def get_epg_etsi_nsd_software_path(self):
        return self.__epgEtsiNsdSoftwarePath

    def set_epg_etsi_nsd_software_path(self, value):
        self.__epgEtsiNsdSoftwarePath = value

    def get_epg_etsi_nsd_version(self):
        return self.__epgEtsiNsdVersion

    def set_epg_etsi_nsd_version(self, value):
        self.__epgEtsiNsdVersion = value

    def get_uds_vf_name(self):
        return self.__uds_vf_name

    def set_uds_vf_name(self, value):
        self.__uds_vf_name = value

    def get_uds_service_unique_id(self):
        return self.__uds_service_unique_id

    def set_uds_service_unique_id(self, value):
        self.__uds_service_unique_id = value

    def get_requirements_unique_id(self):
        return self.__requirements_unique_id

    def set_requirements_unique_id(self, value):
        self.__requirements_unique_id = value

    def get_capabilities_unique_id(self):
        return self.__capabilities_unique_id

    def set_capabilities_unique_id(self, value):
        self.__capabilities_unique_id = value

    def get_ns_composition_id(self):
        return self.__ns_composition_id

    def set_ns_composition_id(self, value):
        self.__ns_composition_id = value

    def get_epg_composition_id(self):
        return self.__epg_composition_id

    def set_epg_composition_id(self, value):
        self.__epg_composition_id = value

    def get_uds_vf_unique_id(self):
        return self.__uds_vf_unique_id

    def set_uds_vf_unique_id(self, value):
        self.__uds_vf_unique_id = value

    # def set_uds_vf_unique_id(self, value):
    #    return self.__uds_vf_unique_id = value

    def get_vfc_onboarded_ids_dict(self):
        return self.__vfc_onboarded_ids_dict

    def set_vfc_onboarded_ids_dict(self, value):
        self.__vfc_onboarded_ids_dict = value

    def get_vfc_certified_ids_dict(self):
        return self.__vfc_certified_ids_dict

    def set_vfc_certified_ids_dict(self, value):
        self.__vfc_certified_ids_dict = value

    def get_uds_hostname(self):
        return self.__uds_hostname

    def set_uds_hostname(self, value):
        self.__uds_hostname = value.strip()

    def get_uds_username(self):
        return self.__uds_username

    def set_uds_username(self, value):
        self.__uds_username = value.strip()

    def get_log_verify_host_url(self):
        return self.__log_verify_host_url

    def set_log_verify_host_url(self, value):
        self.__log_verify_host_url = value

    def get_so_entity_check_user(self):
        return self.__so_entity_check_user

    def set_so_entity_check_user(self, value):
        self.__so_entity_check_user = value

    def get_helm_deployment_name(self):
        return self.__helm_deployment_name

    def set_helm_deployment_name(self, value):
        self.__helm_deployment_name = value

    def get_oss_user_name(self):
        return self.__oss_user_name

    def set_oss_user_name(self, value):
        self.__oss_user_name = value

    def get_ccrc_resource_id(self):
        return self.__ccrc_resource_id

    def set_ccrc_resource_id(self, value):
        self.__ccrc_resource_id = value

    def get_ccrc_ip_address(self):
        return self.__ccrc_ip_address

    def set_ccrc_ip_address(self, value):
        self.__ccrc_ip_address = value

    def get_cnf_vnfm_id(self):
        return self.__cnf_vnfm_id

    def set_cnf_vnfm_id(self, value):
        self.__cnf_vnfm_id = value

    def get_vnf_identifier_id(self):
        return self.__vnf_identifier_id

    def set_vnf_identifier_id(self, value):
        self.__vnf_identifier_id = value

    def get_environment_user_platform(self):
        return self.__environment_user_platform

    def set_environment_user_platform(self, value):
        self.__environment_user_platform = value

    def get_is_vm_vnfm(self):
        return self.__is_vm_vnfm

    def set_is_vm_vnfm(self, value):
        self.__is_vm_vnfm = value.upper()

    def get_base_folder(self):
        return self.__base_folder

    def set_base_folder(self, value):
        self.__base_folder = value + '/'

    def get_enm_deployment_type(self):
        return self.__enm_deployment_type

    def set_enm_deployment_type(self, value):
        self.__enm_deployment_type = value

    def get_so_deployment_type(self):
        return self.__so_deployment_type

    def set_so_deployment_type(self, value):
        self.__so_deployment_type = value.upper()

    def get_bgf_tosca_ip(self):
        return self.__bgf_tosca_ip

    def set_bgf_tosca_ip(self, value):
        self.__bgf_tosca_ip = value

    def get_subsystem_name(self):
        return self.__subsystem_name

    def set_subsystem_name(self, value):
        self.__subsystem_name = value

    def get_vnf_type(self):
        return self.__vnf_type

    def set_vnf_type(self, value):
        self.__vnf_type = value

    def get_vdc_name(self):
        return self.__vdc_name

    def set_vdc_name(self, value):
        self.__vdc_name = value

    def get_ims_vnfd_id(self):
        return self.__ims_vnfd_id

    def set_ims_vnfd_id(self, value):
        self.__ims_vnfd_id = value.strip()

    def get_dummy_mme_path(self):
        return self.__dummy_mme_path

    def set_dummy_mme_path(self, value):
        self.__dummy_mme_path = value.strip()

    def get_network_service_id(self):
        return self.__network_service_id

    def set_network_service_id(self, value):
        self.__network_service_id = value.strip()

    def get_ecm_ns_name(self):
        return self.__ecm_ns_name

    def set_ecm_ns_name(self, value):
        self.__ecm_ns_name = value

    def get_vcisco_gateway_ip(self):
        return self.__vcisco_gateway_ip

    def set_vcisco_gateway_ip(self, value):
        self.__vcisco_gateway_ip = value.strip()

    def get_vcisco_flavour_name(self):
        return self.__vcisco_flavour_name

    def set_vcisco_flavour_name(self, value):
        self.__vcisco_flavour_name = value.strip()

    def get_valid9m_flavour_name(self):
        return self.__valid9m_flavour_name

    def set_valid9m_flavour_name(self, value):
        self.__valid9m_flavour_name = value.strip()

    def get_vcisco_image_name(self):
        return self.__vcisco_image_name

    def set_vcisco_image_name(self, value):
        self.__vcisco_image_name = value.strip()

    def get_valid9m_image_name(self):
        return self.__valid9m_image_name

    def set_valid9m_image_name(self, value):
        self.__valid9m_image_name = value.strip()

    def get_vcisco_image_id(self):
        return self.__vcisco_image_id

    def set_vcisco_image_id(self, value):
        self.__vcisco_image_id = value.strip()

    def get_valid9m_image_id(self):
        return self.__valid9m_image_id

    def set_valid9m_image_id(self, value):
        self.__valid9m_image_id = value.strip()

    def get_dummy_package_name(self):
        return self.__dummy_package_name

    def set_dummy_package_name(self, value):
        self.__dummy_package_name = value

    def get_mme_package_name(self):
        return self.__mme_package_name

    def set_mme_package_name(self, value):
        self.__mme_package_name = value

    def get_mme_packageId(self):
        return self.__mme_packageId

    def set_mme_packageId(self, value):
        self.__mme_packageId = value

    def get_mme_image_names(self):
        return self.__mme_image_names

    def set_mme_image_names(self, value):
        self.__mme_image_names = value.strip()

    def get_mme_image_ids(self):
        return self.__mme_image_ids

    def set_mme_image_ids(self, value):
        self.__mme_image_ids = value.strip()

    def get_mme_flavors(self):
        return self.__mme_flavors

    def set_mme_flavors(self, value):
        self.__mme_flavors = value.strip()

    def get_sbg_version(self):
        return self.__sbg_version

    def set_sbg_version(self, value):
        self.__sbg_version = value

    def get_dcgw_software_path(self):
        return self.__dcgw_software_path

    def set_dcgw_software_path(self, value):
        self.__dcgw_software_path = value

    def get_enm_software_path(self):
        return self.__enm_software_path

    def set_enm_software_path(self, value):
        self.__enm_software_path = value

    def get_bgf_version(self):
        return self.__bgf_version

    def set_bgf_version(self, value):
        self.__bgf_version = value

    def get_mtas_version(self):
        return self.__mtas_version

    def set_mtas_version(self, value):
        self.__mtas_version = value

    def get_cscf_version(self):
        return self.__cscf_version

    def set_cscf_version(self, value):
        self.__cscf_version = value

    def get_mme_version(self):
        return self.__mme_version

    def set_mme_version(self, value):
        self.__mme_version = value

    def get_mme_software_path(self):
        return self.__mme_software_path

    def set_mme_software_path(self, value):
        self.__mme_software_path = value

    def get_service_model_id(self):
        return self.__service_model_id

    def set_service_model_id(self, value):
        self.__service_model_id = value

    def get_nsd_id(self):
        return self.__nsd_id

    def set_nsd_id(self, value):
        self.__nsd_id = value

    def get_epg_software_path(self):
        return self.__epgSoftwarePath

    def set_epg_software_path(self, value):
        self.__epgSoftwarePath = value

    def get_epg_version(self):
        return self.__epgVersion

    def set_epg_version(self, value):
        self.__epgVersion = value

    def get_epg_image_names(self):
        return self.__epg_image_names

    def set_epg_image_names(self, value):
        self.__epg_image_names = value.strip()

    def get_epg_image_ids(self):
        return self.__epg_image_ids

    def set_epg_image_ids(self, value):
        self.__epg_image_ids = value.strip()

    def get_epg_flavors(self):
        return self.__epg_flavors

    def set_epg_flavors(self, value):
        self.__epg_flavors = value.strip()

    def get_vapp_Id(self):
        return self.__vapp_Id

    def set_vapp_Id(self, value):
        self.__vapp_Id = value

    def get_so_host_name(self):
        return self.__so_host_name

    def set_so_host_name(self, value):
        self.__so_host_name = value.strip()

    def get_so_namespace(self):
        return self.__so_namespace

    def set_so_namespace(self, value):
        self.__so_namespace = value.strip()

    def get_vnf_packageId(self):
        return self.__vnf_packageId

    def set_vnf_packageId(self, value):
        self.__vnf_packageId = value

    def get_corelationId(self):
        return self.__corelationId

    def set_corelationId(self, value):
        self.__corelationId = value

    def get_auth_token(self):
        return self.__auth_token

    def set_auth_token(self, value):
        self.__auth_token = value

    def get_vdc_id(self):
        return self.__vdc_id

    def get_epg_vapp_name(self):
        return self.__epg_vapp_name

    def set_epg_vapp_name(self, value):
        self.__epg_vapp_name = value

    def get_project_id(self):
        return self.__project_id

    def set_project_id(self, value):
        self.__project_id = value

    def get_project_system_id(self):
        return self.__project_system_id

    def set_project_system_id(self, value):
        self.__project_system_id = value

    def get_vimzone_id(self):
        return self.__vimzone_id

    def get_vimzone_name(self):
        return self.__vimzone_name

    def set_vdc_id(self, value):
        self.__vdc_id = value

    def set_vimzone_id(self, value):
        self.__vimzone_id = value

    def set_vimzone_name(self, value):
        self.__vimzone_name = value

    def del_vdc_id(self):
        del self.__vdc_id

    def del_vimzone_id(self):
        del self.__vimzone_id

    def del_vimzone_name(self):
        del self.__vimzone_name

    def get_tenant_name(self):
        return self.__tenantName

    def set_tenant_name(self, value):
        self.__tenantName = value

    def del_tenant_name(self):
        del self.__tenantName

    def get_name(self):
        return self.__name

    def get_software_version(self):
        return self.__softwareVersion

    def get_is_public(self):
        return self.__isPublic

    def get_vnf_managers(self):
        return self.__vnfManagers

    def get_vnf_software_version(self):
        return self.__vnfSoftwareVersion

    def get_services_image(self):
        return self.__servicesImage

    def get_services_flavor(self):
        return self.__services_flavor

    def get_external_net_id(self):
        return self.__external_net_id

    def get_external_subnet_cidr(self):
        return self.__external_subnet_cidr

    def get_external_subnet_gateway(self):
        return self.__external_subnet_gateway

    def get_external_ip_for_services_vm(self):
        return self.__external_ip_for_services_vm

    def get_cloud_manager_type(self):
        return self.__cloudManagerType

    def get_oss_type(self):
        return self.__ossType

    def get_oss_master_host_name(self):
        return self.__ossMasterHostName

    def get_oss_master_host_ip(self):
        return self.__ossMasterHostIP

    def get_oss_notification_service_host(self):
        return self.__ossNotificationServiceHost

    def get_oss_notification_service_ip(self):
        return self.__ossNotificationServiceIP

    def set_name(self, value):
        self.__name = value

    def set_software_version(self, value):
        self.__softwareVersion = value

    def set_is_public(self, value):
        self.__isPublic = value

    def set_vnf_managers(self, value):
        self.__vnfManagers = value

    def set_vnf_software_version(self, value):
        self.__vnfSoftwareVersion = value

    def set_services_image(self, value):
        self.__servicesImage = value

    def set_services_flavor(self, value):
        self.__services_flavor = value

    def set_external_net_id(self, value):
        self.__external_net_id = value

    def set_external_subnet_cidr(self, value):
        self.__external_subnet_cidr = value

    def set_external_subnet_gateway(self, value):
        self.__external_subnet_gateway = value

    def set_external_ip_for_services_vm(self, value):
        self.__external_ip_for_services_vm = value

    def set_cloud_manager_type(self, value):
        self.__cloudManagerType = value

    def set_oss_type(self, value):
        self.__ossType = value

    def set_oss_master_host_name(self, value):
        self.__ossMasterHostName = value

    def set_oss_master_host_ip(self, value):
        self.__ossMasterHostIP = value

    def set_oss_notification_service_host(self, value):
        self.__ossNotificationServiceHost = value

    def set_oss_notification_service_ip(self, value):
        self.__ossNotificationServiceIP = value

    def get_external_ip_for_services_vm_to_scale(self):
        return self.__externalIpForServicesVmToScale

    def set_sub_network_system_id(self, value):
        self.__sub_network_system_id = value

    def get_sub_network_system_id(self):
        return self.__sub_network_system_id

    def set_external_network_system_id(self, value):
        self.__external_network_system_id = value

    def get_external_network_system_id(self):
        return self.__external_network_system_id

    def set_external_ip_for_services_vm_to_scale(self, value):
        self.__externalIpForServicesVmToScale = value

    def get_is_ccd(self):
        return self.__is_ccd

    def set_is_ccd(self, value):
        self.__is_ccd = True if value.strip().lower() == 'true' else False

    def get_cnf_ns_instance_id(self):
        return self.__cnf_ns_instance_id

    def set_cnf_ns_instance_id(self, value):
        self.__cnf_ns_instance_id = value

    def get_ccrc_upgrade_vnfd_id(self):
        return self.__ccrc_upgrade_vnfd_id

    def set_ccrc_upgrade_vnfd_id(self, value):
        self.__ccrc_upgrade_vnfd_id = value

    def get_ccrc_deploy_vnfd_id(self):
        return self.__ccrc_deploy_vnfd_id

    def set_ccrc_deploy_vnfd_id(self, value):
        self.__ccrc_deploy_vnfd_id = value

    def set_tosca_epg_ns_instance_id(self, value):
        self.__tosca_epg_ns_instance_id = value

    def get_tosca_epg_ns_instance_id(self):
        return self.__tosca_epg_ns_instance_id

    def set_tosca_epg_vapp(self, value):
        self.__tosca_epg_vapp = value

    def get_tosca_epg_vapp(self):
        return self.__tosca_epg_vapp

    def set_etsi_tepg_ns_instance_id(self, value):
        self.__etsi_tepg_ns_instance_id = value

    def get_etsi_tepg_ns_instance_id(self):
        return self.__etsi_tepg_ns_instance_id

    def set_etsi_tosca_epg_vapp(self, value):
        self.__etsi_tosca_epg_vapp = value

    def get_etsi_tosca_epg_vapp(self):
        return self.__etsi_tosca_epg_vapp

    def set_vmvnfm_pod_0(self, value):
        self.__vmvnfm_pod_0 = value

    def get_vmvnfm_pod_0(self):
        return self.__vmvnfm_pod_0

    def set_vmvnfm_pod_1(self, value):
        self.__vmvnfm_pod_1 = value

    def get_vmvnfm_pod_1(self):
        return self.__vmvnfm_pod_1

    def del_name(self):
        del self.__name

    def del_software_version(self):
        del self.__softwareVersion

    def del_is_public(self):
        del self.__isPublic

    def del_vnf_managers(self):
        del self.__vnfManagers

    def del_vnf_software_version(self):
        del self.__vnfSoftwareVersion

    def del_services_image(self):
        del self.__servicesImage

    def del_services_flavor(self):
        del self.__services_flavor

    def del_external_net_id(self):
        del self.__external_net_id

    def del_external_subnet_cidr(self):
        del self.__external_subnet_cidr

    def del_external_subnet_gateway(self):
        del self.__external_subnet_gateway

    def del_external_ip_for_services_vm(self):
        del self.__external_ip_for_services_vm

    def del_cloud_manager_type(self):
        del self.__cloudManagerType

    def del_oss_type(self):
        del self.__ossType

    def del_oss_master_host_name(self):
        del self.__ossMasterHostName

    def del_oss_master_host_ip(self):
        del self.__ossMasterHostIP

    def del_oss_notification_service_host(self):
        del self.__ossNotificationServiceHost

    def del_oss_notification_service_ip(self):
        del self.__ossNotificationServiceIP

    def get_json_file_data(self):
        self.block_data = {
            "servicesImage": self.get_services_image(self),
            "services_flavor": self.get_services_flavor(self),
            "ip_version": 4,
            "services_vm_count": 1,
            "external_net_id": self.get_external_net_id(self),
            "external_subnet_cidr": self.get_external_subnet_cidr(self),
            "external_subnet_gateway": self.get_external_subnet_gateway(self),
            "external_ip_for_services_vm": self.get_external_ip_for_services_vm(self),
            "cloudManagerType": self.get_cloud_manager_type(self),
            "ossType": self.get_oss_type(self),
            "ossMasterHostName": self.get_oss_master_host_name(self),
            "ossMasterHostIP": self.get_oss_master_host_ip(self),
            "ossNotificationServiceHost": self.get_oss_notification_service_host(self),
            "ossNotificationServiceIP": self.get_oss_notification_service_ip(self),
            "retry": True,
            "retryTimes": 5,
            "ossUserName": "administrator"
        }

        return self.block_data

    def set_json_file_data(self, value):
        self.block_data = value

    name = property(get_name, set_name, del_name, "name's docstring")
    softwareVersion = property(get_software_version, set_software_version, del_software_version,
                               "softwareVersion's docstring")
    isPublic = property(get_is_public, set_is_public, del_is_public, "isPublic's docstring")
    vnfManagers = property(get_vnf_managers, set_vnf_managers, del_vnf_managers, "vnfManagers's docstring")
    vnfSoftwareVersion = property(get_vnf_software_version, set_vnf_software_version, del_vnf_software_version,
                                  "vnfSoftwareVersion's docstring")
    servicesImage = property(get_services_image, set_services_image, del_services_image, "servicesImage's docstring")
    services_flavor = property(get_services_flavor, set_services_flavor, del_services_flavor,
                               "services_flavor's docstring")
    external_net_id = property(get_external_net_id, set_external_net_id, del_external_net_id,
                               "external_net_id's docstring")
    external_subnet_cidr = property(get_external_subnet_cidr, set_external_subnet_cidr, del_external_subnet_cidr,
                                    "external_subnet_cidr's docstring")
    external_subnet_gateway = property(get_external_subnet_gateway, set_external_subnet_gateway,
                                       del_external_subnet_gateway, "external_subnet_gateway's docstring")
    external_ip_for_services_vm = property(get_external_ip_for_services_vm, set_external_ip_for_services_vm,
                                           del_external_ip_for_services_vm, "external_ip_for_services_vm's docstring")
    cloudManagerType = property(get_cloud_manager_type, set_cloud_manager_type, del_cloud_manager_type,
                                "cloudManagerType's docstring")
    ossType = property(get_oss_type, set_oss_type, del_oss_type, "ossType's docstring")
    ossMasterHostName = property(get_oss_master_host_name, set_oss_master_host_name, del_oss_master_host_name,
                                 "ossMasterHostName's docstring")
    ossMasterHostIP = property(get_oss_master_host_ip, set_oss_master_host_ip, del_oss_master_host_ip,
                               "ossMasterHostIP's docstring")
    ossNotificationServiceHost = property(get_oss_notification_service_host, set_oss_notification_service_host,
                                          del_oss_notification_service_host, "ossNotificationServiceHost's docstring")
    ossNotificationServiceIP = property(get_oss_notification_service_ip, set_oss_notification_service_ip,
                                        del_oss_notification_service_ip, "ossNotificationServiceIP's docstring")
    tenantName = property(get_tenant_name, set_tenant_name, del_tenant_name, "tenantName's docstring")
    vdc_id = property(get_vdc_id, set_vdc_id, del_vdc_id, "vdc_id's docstring")
    vimzone_id = property(get_vimzone_id, set_vimzone_id, del_vimzone_id, "vimzone_id's docstring")
    vimzone_name = property(get_vimzone_name, set_vimzone_name, del_vimzone_name, "vimzone_name's docstring")
