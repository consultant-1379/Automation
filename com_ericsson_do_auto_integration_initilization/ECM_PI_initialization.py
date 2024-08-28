


'''
Created on 10 sep 2018

@author: eiaavij

'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_model.Ecm_PI import Ecm_PI
from com_ericsson_do_auto_integration_model.EPIS import EPIS
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
import json

log = Logger.get_logger('ECM_PI_intialization.py')

class ECM_PI_Initialization():
    

    model_objects = {}
    #user_input_file ='user_input.json'

    def get_model_objects(self,key):
        return  self.model_objects[key]
    
    def get_json_list_objects(self,key):
        return self.json_list_objects[key]
    
    def store_ecm_pi(self,file_data):
        
        log.info('Going to collect post ECM installation data ')
        
        # setting up alalcation pools ip for external network
        Ecm_PI.set_allocation_pools_ip(Ecm_PI, file_data['ALLOCATION_POOLS_IP'])
        Ecm_PI.set_ecm_host_name(Ecm_PI, file_data['ENVIRONMENT'])
        Ecm_PI.set_ecm_host_blade_ip(Ecm_PI, file_data['ECM_Host_Blade_IP'])
        Ecm_PI.set_ecm_host_blade_username(Ecm_PI, file_data['ECM_Host_Blade_username'])
        Ecm_PI.set_ecm_host_blade_password(Ecm_PI, file_data['ECM_Host_Blade_Password'])
        # Below is used in all curl command 
        Ecm_PI.set_core_vm_ip(Ecm_PI,file_data['CORE_VM_APPLICATION_SERVICE_IP'])
        Ecm_PI.set_core_vm_hostname(Ecm_PI,file_data['CORE_VM_Hostname'])
        Ecm_PI.set_vm_deployment_name(Ecm_PI, file_data['DEPLOYMENT_NAME'])        
        Ecm_PI.set_core_vm_username(Ecm_PI,file_data['CORE_VM_Username'])
        Ecm_PI.set_core_vm_password(Ecm_PI,file_data['CORE_VM_Password'])        
        Ecm_PI.set_vcisco_management_ip(Ecm_PI,file_data['VCISCO_MANAGEMENT_IP'])
        Ecm_PI.set_vcisco_management_username(Ecm_PI,file_data['VCISCO_MANAGEMENT_USERNAME'])
        Ecm_PI.set_vcisco_management_password(Ecm_PI,file_data['VCISCO_MANAGEMENT_PASSWORD'])
        Ecm_PI.set_activation_vm_ip(Ecm_PI,file_data['ACTIVATION_VM_IP'])
        Ecm_PI.set_activation_vm_username(Ecm_PI,file_data['ACTIVATION_VM_USERNAME'])
        Ecm_PI.set_activation_vm_password(Ecm_PI,file_data['ACTIVATION_VM_PASSWORD'])
        Ecm_PI.set_activation_gui_username(Ecm_PI,file_data['ACTIVATION_GUI_USERNAME'])
        Ecm_PI.set_activation_gui_password(Ecm_PI,file_data['ACTIVATION_GUI_PASSWORD'])        
        Ecm_PI.set_asr_device_name(Ecm_PI,file_data['ASR_DEVICE_NAME']) 
        Ecm_PI.set_dcgw_ne_name(Ecm_PI,file_data['DCGW_NE_NAME'])
        # Below is used for site creation login in case of HA deployment in ECM_POST_INSTALLATION.py and DC Gateway logic
        Ecm_PI.set_core_vm_ha_ip(Ecm_PI,file_data['CORE_VM_IP'])
        # IN HA Env we have 2 core VM , this is the second IP of Core VM, used in ECM session update job
        Ecm_PI.set_core_vm_2_ha_ip(Ecm_PI,file_data['CORE_VM_2_IP'])
        Ecm_PI.set_deployment_type(Ecm_PI,file_data['DEPLOYMENT_TYPE'])
        Ecm_PI.set_rdb_vm_ip(Ecm_PI,file_data['RDB_VM_IP'])
        Ecm_PI.set_rdb_vm_username(Ecm_PI,file_data['RDB_VM_USERNAME'])
        Ecm_PI.set_rdb_vm_password(Ecm_PI,file_data['RDB_VM_PASSWORD']) 
           
        
        
        self.model_objects['ECMPI'] = Ecm_PI
        log.info('Finished to collect post ECM installation data')


    def store_epis_data(self,file_data):

        log.info('Going to collect data ')
        
        EPIS.set_flavour_name(EPIS,file_data['SERVICES_FLAVOR'])
        EPIS.set_core_vm_hostname(Ecm_PI,file_data['CORE_VM_Hostname'])
        EPIS.set_tenant_name(EPIS,file_data['TENANT_NAME'])
        EPIS.set_vimzone_name(EPIS,file_data['VIM_NAME_FOR_CLOUD'])
        EPIS.set_image_id(EPIS,file_data['SERVICES_IMAGE_ID'])
        EPIS.set_image_name(EPIS,file_data['SERVICES_IMAGE_NAME'])
        EPIS.set_site_name(EPIS, file_data['SITE_NAME'])
        EPIS.set_project_name(EPIS, file_data['PROJECT_NAME'])
        EPIS.set_external_network_name(EPIS, file_data['EXTERNAL_NETWORK_NAME'])
        EPIS.set_openstack_ip(EPIS,file_data['OPENSTACK_IP'])
        EPIS.set_openstack_username(EPIS,file_data['OPENSTACK_USERNAME'])
        EPIS.set_openstack_password(EPIS,file_data['OPENSTACK_PASSWORD'])
        EPIS.set_openrc_filename(EPIS,file_data['OPENRC_FILENAME'])
        EPIS.set_segmentation_id(EPIS,file_data['NETWORK_SEGMENTATION_ID'])
        EPIS.set_network_ipv4_range(EPIS,file_data['NETWORK_IPV4_RANGE'])
        EPIS.set_network_ipv6_range(EPIS,file_data['NETWORK_IPV6_RANGE'])
        EPIS.set_static_project(EPIS,file_data['CLOUD_STATIC_PROJECT_NAME'])
        EPIS.set_static_project_username(EPIS,file_data['CLOUD_STATIC_PROJECT_USERNAME'])
        EPIS.set_static_project_password(EPIS,file_data['CLOUD_STATIC_PROJECT_PASSWORD'])
        EPIS.set_cloud_manager_type(EPIS, file_data['CLOUD_TYPE'])
        EPIS.set_sync_cloud_manager_type(EPIS, file_data['SYNC_CLOUD_TYPE'])
        EPIS.set_sync_vim_availability_zone(EPIS, file_data['SYNC_VIM_AVAILABILITY_ZONE'])
        EPIS.set_sync_tenant_name(EPIS,file_data['SYNC_TENANT_NAME'])
        EPIS.set_sync_tenant_type(EPIS,file_data['SYNC_TENANT_TYPE'])
        EPIS.set_sync_tenant_username(EPIS,file_data['SYNC_TENANT_USERNAME'])
        EPIS.set_sync_tenant_password(EPIS,file_data['SYNC_TENANT_PASSWORD'])
        EPIS.set_sync_vimzone_name(EPIS,file_data['SYNC_VIM_NAME_FOR_CLOUD'])
        EPIS.set_sync_openrc_filename(EPIS,file_data['SYNC_OPENRC_FILENAME'])
        EPIS.set_sync_cloud_hostname(EPIS,file_data['SYNC_CLOUD_HOSTNAME'])
        EPIS.set_sync_cloud_host_ip(EPIS,file_data['SYNC_CLOUD_HOST_IP'])
        EPIS.set_sync_atlas_hostname(EPIS,file_data['SYNC_ATLAS_HOSTNAME'])
        EPIS.set_sync_atlas_host_ip(EPIS,file_data['SYNC_ATLAS_HOST_IP'])
        EPIS.set_existing_project_name(EPIS, file_data['EXISTING_PROJECT_NAME'])
        EPIS.set_existing_project_admin_username(EPIS, file_data['EXISTING_PROJECT_ADMIN_USERNAME'])
        EPIS.set_existing_project_admin_password(EPIS, file_data['EXISTING_PROJECT_ADMIN_PASSWORD'])
        EPIS.set_existing_project_user_username(EPIS, file_data['EXISTING_PROJECT_USER_USERNAME'])
        EPIS.set_existing_project_user_password(EPIS, file_data['EXISTING_PROJECT_USER_PASSWORD'])
        EPIS.set_sync_vim_url(EPIS, file_data['SYNC_VIM_URL'])
        #keystone is used in Integration job
        EPIS.set_key_stone(EPIS, file_data['KEY_STONE'])
        #vimurl is used in cee cleanup openrc file creation
        EPIS.set_vim_url(EPIS, file_data['VIM_URL'])
        EPIS.set_cn_env_name(EPIS, file_data['CN_ENV_NAME'])
        EPIS.set_cn_cmdb_password(EPIS, file_data['CN_CMDB_PASSWORD'])
        EPIS.set_ram_cpu_storage(EPIS, file_data['RAM_CPU_STORAGE'])
        EPIS.set_external_network_vim_id(EPIS, file_data['EXTERNAL_NETWORK_VIM_ID'])
        EPIS.set_network_subnet_vim_id(EPIS, file_data['NETWORK_SUBNET_VIM_ID'])
        self.model_objects['EPIS'] = EPIS
        log.info('Finished to collect  data')

        
    def store_user_inputs(self,user_input_file):
        log.info('Going to collect User_Inputs for ECM post installation tasks')
        
        try:
            
            with open(user_input_file, 'r') as user_input:
            
                file_data = json.load(user_input)
            
                self.store_ecm_pi(self,file_data)
                self.store_epis_data(self,file_data)
                Initialization_script.store_ecm_core_data(Initialization_script,file_data,False)
               
               
                
        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : '+user_input_file)
            assert False
        log.info('Finished to collect User_Inputs for ECM post installation tasks')
        