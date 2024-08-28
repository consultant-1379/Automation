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

class EPIS(object):

    def get_sync_tenant_type(self):
        return self.__sync_tenant_type


    def set_sync_tenant_type(self, value):
        self.__sync_tenant_type = value


    def get_external_network_name(self):
        return self.__external_network_name


    def set_external_network_name(self, value):
        self.__external_network_name = value

    def get_external_network_vim_id(self):
        return self.__external_network_vim_id


    def set_external_network_vim_id(self, value):
        self.__external_network_vim_id = value

    def get_network_subnet_vim_id(self):
        return self.__network_subnet_vim_id


    def set_network_subnet_vim_id(self, value):
        self.__network_subnet_vim_id = value

    def get_sync_cloud_host_ip(self):
        return self.__sync_cloud_host_ip


    def set_sync_cloud_host_ip(self, value):
        self.__sync_cloud_host_ip = value.strip()


    def get_sync_cloud_hostname(self):
        return self.__sync_cloud_hostname


    def set_sync_cloud_hostname(self, value):
        self.__sync_cloud_hostname = value


    def get_sync_atlas_host_ip(self):
        return self.__sync_atlas_host_ip


    def set_sync_atlas_host_ip(self, value):
        self.__sync_atlas_host_ip = value.strip()


    def get_sync_atlas_hostname(self):
        return self.__sync_atlas_hostname


    def set_sync_atlas_hostname(self, value):
        self.__sync_atlas_hostname = value


    def get_key_stone(self):
        return self.__key_stone


    def set_key_stone(self, value):
        self.__key_stone = value


    def get_vim_url(self):
        return self.__vim_url


    def set_vim_url(self, value):
        self.__vim_url = value


    def get_sync_vim_url(self):
        return self.__sync_vim_url


    def set_sync_vim_url(self, value):
        self.__sync_vim_url = value


    def get_sync_tenant_name(self):
        return self.__sync_tenant_name


    def set_sync_tenant_name(self, value):
        self.__sync_tenant_name = value


    def get_sync_tenant_username(self):
        return self.__sync_tenant_username


    def set_sync_tenant_username(self, value):
        self.__sync_tenant_username = value


    def get_sync_tenant_password(self):
        return self.__sync_tenant_password


    def set_sync_tenant_password(self, value):
        self.__sync_tenant_password = value


    def get_sync_vimzone_name(self):
        return self.__sync_vimzone_name


    def set_sync_vimzone_name(self, value):
        self.__sync_vimzone_name = value


    def get_existing_project_name(self):
        return self.__existing_project_name


    def set_existing_project_name(self, value):
        self.__existing_project_name = value


    def get_existing_project_admin_username(self):
        return self.__existing_project_admin_username


    def set_existing_project_admin_username(self, value):
        self.__existing_project_admin_username = value


    def get_existing_project_admin_password(self):
        return self.__existing_project_admin_password


    def set_existing_project_admin_password(self, value):
        self.__existing_project_admin_password = value


    def get_existing_project_user_username(self):
        return self.__existing_project_user_username


    def set_existing_project_user_username(self, value):
        self.__existing_project_user_username = value


    def get_existing_project_user_password(self):
        return self.__existing_project_user_password


    def set_existing_project_user_password(self, value):
        self.__existing_project_user_password = value


    def get_sync_openrc_filename(self):
        return self.__sync_openrc_filename


    def set_sync_openrc_filename(self, value):
        self.__sync_openrc_filename = value


    def get_cloud_manager_type(self):
        return self.__cloudManagerType


    def set_cloud_manager_type(self, value):
        self.__cloudManagerType = value


    def get_sync_cloud_manager_type(self):
        return self.__synccloudManagerType


    def set_sync_cloud_manager_type(self, value):
        self.__synccloudManagerType = value


    def get_static_project(self):
        return self.__static_project


    def set_static_project(self, value):
        self.__static_project = value


    def get_static_project_username(self):
        return self.__static_project_username


    def set_static_project_username(self, value):
        self.__static_project_username = value


    def get_static_project_password(self):
        return self.__static_project_password


    def set_static_project_password(self, value):
        self.__static_project_password = value


    def get_project_exists(self):
        return self.__project_exists


    def set_project_exists(self, value):
        self.__project_exists = value


    def get_segmentation_id(self):
        return self.__segmentation_id


    def set_segmentation_id(self, value):
        self.__segmentation_id = value.strip()


    def get_network_ipv4_range(self):
        return self.__network_ipv4_range


    def set_network_ipv4_range(self, value):
        self.__network_ipv4_range = value.strip()


    def get_network_ipv6_range(self):
        return self.__network_ipv6_range


    def set_network_ipv6_range(self, value):
        self.__network_ipv6_range = value.strip()


    def get_network_gatway_ip(self):
        return self.__network_gatway_ip


    def set_network_gatway_ip(self, value):
        self.__network_gatway_ip = value.strip()


    def get_openrc_filename(self):
        return self.__openrc_filename


    def set_openrc_filename(self, value):
        self.__openrc_filename = value.strip()


    def get_openstack_ip(self):
        return self.__openstack_ip


    def set_openstack_ip(self, value):
        self.__openstack_ip = value.strip()


    def get_openstack_username(self):
        return self.__openstack_username


    def set_openstack_username(self, value):
        self.__openstack_username = value.strip()


    def get_openstack_password(self):
        return self.__openstack_password


    def set_openstack_password(self, value):
        self.__openstack_password = value.strip()


    def get_site_name(self):
        return self.__site_name


    def set_site_name(self, value):
        self.__site_name = value.strip()


    def get_project_name(self):
        return self.__project_name


    def set_project_name(self, value):
        self.__project_name = value.strip()


    def get_vimzone_name(self):
        return self.__vimzone_name


    def set_vimzone_name(self, value):
        self.__vimzone_name = value.strip()


    def get_tenant_name(self):
        return self.__tenant_name


    def set_tenant_name(self, value):
        self.__tenant_name = value.strip()


    def get_flavour_name(self):
        return self.__flavour_name


    def set_flavour_name(self, value):
        self.__flavour_name = value.strip()


    def get_image_name(self):
        return self.__image_name


    def set_image_name(self, value):
        self.__image_name = value.strip()


    def get_image_id(self):
        return self.__image_id


    def set_image_id(self, value):
        self.__image_id = value.strip()


    def set_sync_vim_availability_zone(self, value):
        self.__sync_vim_availability_zone = value


    def get_sync_vim_availability_zone(self):
        return self.__sync_vim_availability_zone


    def get_vdc_id(self):
        return self.__vdc_id


    def set_vdc_id(self, value):
        self.__vdc_id = value


    def get_core_vm_hostname(self):
        return self.__CORE_VM_Hostname


    def set_core_vm_hostname(self, value):
        self.__CORE_VM_Hostname = value.strip()


    def get_sync_cloud_hostname(self):
        return self.__sync_cloud_hostname


    def set_sync_cloud_hostname(self, value):
        self.__sync_cloud_hostname = value


    def get_sync_atlas_host_ip(self):
        return self.__sync_atlas_host_ip


    def set_sync_atlas_host_ip(self, value):
        self.__sync_atlas_host_ip = value.strip()


    def get_sync_atlas_hostname(self):
        return self.__sync_atlas_hostname


    def set_sync_atlas_hostname(self, value):
        self.__sync_atlas_hostname = value


    def get_key_stone(self):
        return self.__key_stone


    def set_key_stone(self, value):
        self.__key_stone = value


    def get_vim_url(self):
        return self.__vim_url


    def set_vim_url(self, value):
        self.__vim_url = value


    def get_sync_vim_url(self):
        return self.__sync_vim_url


    def set_sync_vim_url(self, value):
        self.__sync_vim_url = value


    def get_sync_tenant_name(self):
        return self.__sync_tenant_name


    def set_sync_tenant_name(self, value):
        self.__sync_tenant_name = value


    def get_sync_tenant_username(self):
        return self.__sync_tenant_username


    def set_sync_tenant_username(self, value):
        self.__sync_tenant_username = value


    def get_sync_tenant_password(self):
        return self.__sync_tenant_password


    def set_sync_tenant_password(self, value):
        self.__sync_tenant_password = value


    def get_sync_vimzone_name(self):
        return self.__sync_vimzone_name


    def set_sync_vimzone_name(self, value):
        self.__sync_vimzone_name = value


    def get_existing_project_name(self):
        return self.__existing_project_name


    def set_existing_project_name(self, value):
        self.__existing_project_name = value


    def get_existing_project_admin_username(self):
        return self.__existing_project_admin_username


    def set_existing_project_admin_username(self, value):
        self.__existing_project_admin_username = value


    def get_existing_project_admin_password(self):
        return self.__existing_project_admin_password


    def set_existing_project_admin_password(self, value):
        self.__existing_project_admin_password = value


    def get_existing_project_user_username(self):
        return self.__existing_project_user_username


    def set_existing_project_user_username(self, value):
        self.__existing_project_user_username = value


    def get_existing_project_user_password(self):
        return self.__existing_project_user_password


    def set_existing_project_user_password(self, value):
        self.__existing_project_user_password = value


    def get_sync_openrc_filename(self):
        return self.__sync_openrc_filename


    def set_sync_openrc_filename(self, value):
        self.__sync_openrc_filename = value


    def get_cloud_manager_type(self):
        return self.__cloudManagerType


    def set_cloud_manager_type(self, value):
        self.__cloudManagerType = value


    def get_sync_cloud_manager_type(self):
        return self.__synccloudManagerType


    def set_sync_cloud_manager_type(self, value):
        self.__synccloudManagerType = value


    def get_static_project(self):
        return self.__static_project


    def set_static_project(self, value):
        self.__static_project = value


    def get_static_project_username(self):
        return self.__static_project_username


    def set_static_project_username(self, value):
        self.__static_project_username = value


    def get_static_project_password(self):
        return self.__static_project_password


    def set_static_project_password(self, value):
        self.__static_project_password = value


    def get_project_exists(self):
        return self.__project_exists


    def set_project_exists(self, value):
        self.__project_exists = value


    def get_segmentation_id(self):
        return self.__segmentation_id


    def set_segmentation_id(self, value):
        self.__segmentation_id = value.strip()


    def get_network_ipv4_range(self):
        return self.__network_ipv4_range


    def set_network_ipv4_range(self, value):
        self.__network_ipv4_range = value.strip()


    def get_network_ipv6_range(self):
        return self.__network_ipv6_range


    def set_network_ipv6_range(self, value):
        self.__network_ipv6_range = value.strip()


    def get_network_gatway_ip(self):
        return self.__network_gatway_ip


    def set_network_gatway_ip(self, value):
        self.__network_gatway_ip = value.strip()


    def get_openrc_filename(self):
        return self.__openrc_filename


    def set_openrc_filename(self, value):
        self.__openrc_filename = value.strip()


    def get_openstack_ip(self):
        return self.__openstack_ip


    def set_openstack_ip(self, value):
        self.__openstack_ip = value.strip()


    def get_openstack_username(self):
        return self.__openstack_username


    def set_openstack_username(self, value):
        self.__openstack_username = value.strip()


    def get_openstack_password(self):
        return self.__openstack_password


    def set_openstack_password(self, value):
        self.__openstack_password = value.strip()


    def get_site_name(self):
        return self.__site_name


    def set_site_name(self, value):
        self.__site_name = value.strip()


    def get_project_name(self):
        return self.__project_name


    def set_project_name(self, value):
        self.__project_name = value.strip()


    def get_vimzone_name(self):
        return self.__vimzone_name


    def set_vimzone_name(self, value):
        self.__vimzone_name = value.strip()


    def get_tenant_name(self):
        return self.__tenant_name


    def set_tenant_name(self, value):
        self.__tenant_name = value.strip()


    def get_flavour_name(self):
        return self.__flavour_name


    def set_flavour_name(self, value):
        self.__flavour_name = value.strip()


    def get_image_name(self):
        return self.__image_name


    def set_image_name(self, value):
        self.__image_name = value.strip()


    def get_image_id(self):
        return self.__image_id


    def set_image_id(self, value):
        self.__image_id = value.strip()


    def set_sync_vim_availability_zone(self, value):
        self.__sync_vim_availability_zone = value


    def get_sync_vim_availability_zone(self):
        return self.__sync_vim_availability_zone


    def get_vdc_id(self):
        return self.__vdc_id


    def set_vdc_id(self, value):
        self.__vdc_id = value

    def set_cn_env_name(self, value):
        self.__cn_env_name = value.strip()

    def get_cn_env_name(self):
        return self.__cn_env_name

    def set_cn_cmdb_password(self, value):
        self.__cn_cmdb_password = value.strip()

    def get_cn_cmdb_password(self):
        return self.__cn_cmdb_password

    def get_ram_cpu_storage(self):
        return self.__ram_cpu_storage

    def set_ram_cpu_storage(self, value):
        self.__ram_cpu_storage = value.strip()
