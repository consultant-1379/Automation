'''
Created on 22 Aug 2018

@author: emaidns
'''


class Ecm_core(object):
    
    def get_vm_vnfm_namespace(self):
        return self.__vm_vnfm_namespace

    def set_vm_vnfm_namespace(self, value):
        self.__vm_vnfm_namespace = value    
    
    def get_ccd1_vm_vnfm_director_ip(self):
        return self.__ccd1_vm_vnfm_director_ip

    def set_ccd1_vm_vnfm_director_ip(self, value):
        self.__ccd1_vm_vnfm_director_ip = value

    def get_ccd1_vm_vnfm_director_username(self):
        return self.__ccd1_vm_vnfm_director_username

    def set_ccd1_vm_vnfm_director_username(self, value):
        self.__ccd1_vm_vnfm_director_username = value
    
    def get_cism_register_url(self):
        return self.__cism_register_url

    def set_cism_register_url(self, value):
        self.__cism_register_url = value
     
    def get_evnfm_hostname(self):
        return self.__evnfm_hostname

    def set_evnfm_hostname(self, value):
        self.__evnfm_hostname = value

    def get_evnfm_auth_username(self):
        return self.__evnfm_auth_username

    def set_evnfm_auth_username(self, value):
        self.__evnfm_auth_username = value

    def get_evnfm_auth_password(self):
        return self.__evnfm_auth_password

    def set_evnfm_auth_password(self, value):
        self.__evnfm_auth_password = value
  
    def get_vm_vnfm_director_ip(self):
        return self.__vm_vnfm_director_ip

    def set_vm_vnfm_director_ip(self, value):
        self.__vm_vnfm_director_ip = value
        
    def get_cism_cluster_ip(self):
        return self.__cism_cluster_ip

    def set_cism_cluster_ip(self, value):
        self.__cism_cluster_ip = value  
    
    def get_vm_vnfm_director_username(self):
        return self.__vm_vnfm_director_username

    def set_vm_vnfm_director_username(self, value):
        self.__vm_vnfm_director_username = value

    def get_abcd_vm_ip(self):
        return self.__abcd_vm_ip
    
    def set_abcd_vm_ip(self, value):
        self.__abcd_vm_ip = value.strip()
    
    def get_abcd_vm_username(self):
        return self.__abcd_vm_username
    
    def set_abcd_vm_username(self, value):
        self.__abcd_vm_username = value.strip()
    
    def get_abcd_vm_password(self):
        return self.__abcd_vm_password
    
    def set_abcd_vm_password(self, value):
        self.__abcd_vm_password = value.strip()
    
    def get_vnf_lcm_dynamic_servicedb_ip(self):
        return self.__VNF_LCM_dynamic_Servicedb_IP
    
    def set_vnf_lcm_dynamic_servicedb_ip(self, value):
        self.__VNF_LCM_dynamic_Servicedb_IP = value.strip()
    
    
    def get_vnf_lcm_dynamic_service_ip1(self):
        return self.__VNF_LCM_dynamic_Service_IP1
   
    def set_vnf_lcm_dynamic_service_ip1(self, value):
        self.__VNF_LCM_dynamic_Service_IP1 = value.strip()

    def get_vnf_lcm_dynamic_service_ip(self):
        return self.__VNF_LCM_dynamic_Service_IP

    def set_vnf_lcm_dynamic_service_ip(self, value):
        self.__VNF_LCM_dynamic_Service_IP = value.strip()
    
    
    def get_ecm_gui_username(self):
        return self.__ecm_gui_username

    def set_ecm_gui_username(self, value):
        self.__ecm_gui_username = value.strip()

    def get_ecm_gui_password(self):
        return self.__ecm_gui_password

    def set_ecm_gui_password(self, value):
        self.__ecm_gui_password = value.strip()

    def get_enviornment(self):
        return self.__enviornment

    def set_enviornment(self, value):
        self.__enviornment = value.strip()


    def get_rpm_bundle_link(self):
        return self.__rpm_bundle_link

    def set_rpm_bundle_link(self, value):
        self.__rpm_bundle_link = value.strip()


    def get_discovery_bundle_link(self):
        return self.__discovery_bundle_link

    def set_discovery_bundle_link(self, value):
        self.__discovery_bundle_link = value.strip()

    def get_core_vm_hostname(self):
        return self.__core_vm_hostname

    def set_core_vm_hostname(self, value):
        self.__core_vm_hostname = value.strip()


    def get_enm_hostname(self):
        return self.__enm_hostname

    def set_enm_hostname(self, value):
        self.__enm_hostname = value.strip()


    def get_multi_enm_hostname(self):
        return self.__multi_enm_hostname

    def set_multi_enm_hostname(self, value):
        self.__multi_enm_hostname = value.strip()



    def get_vnf_lcm_servicedb_ip(self):
        return self.__VNF_LCM_Servicedb_IP


    def get_vnf_lcm_servicedb_username(self):
        return self.__VNF_LCM_Servicedb_Username


    def get_vnf_lcm_servicedb_password(self):
        return self.__VNF_LCM_Servicedb_Password


    def set_vnf_lcm_servicedb_ip(self, value):
        self.__VNF_LCM_Servicedb_IP = value.strip()


    def set_vnf_lcm_servicedb_username(self, value):
        self.__VNF_LCM_Servicedb_Username = value.strip()


    def set_vnf_lcm_servicedb_password(self, value):
        self.__VNF_LCM_Servicedb_Password = value.strip()

    
    def get_ecm_host_blade_ip(self):
        return self.__ECM_Host_Blade_IP


    def get_ecm_host_blade_username(self):
        return self.__ECM_Host_Blade_username


    def get_ecm_host_blade_password(self):
        return self.__ECM_Host_Blade_Password


    def get_core_vm_ip(self):
        return self.__CORE_VM_IP


    def set_ecm_host_blade_ip(self, value):
        self.__ECM_Host_Blade_IP = value.strip()


    def set_ecm_host_blade_username(self, value):
        self.__ECM_Host_Blade_username = value.strip()


    def set_ecm_host_blade_password(self, value):
        self.__ECM_Host_Blade_Password = value.strip()


    def set_core_vm_ip(self, value):
        self.__CORE_VM_IP = value.strip()

    def set_is_cloudnative(self, value):
        self.__is_cloudnative = value

    def get_is_cloudnative(self):
        return self.__is_cloudnative

    def set_ecm_certificate_path(self, value):
        self.__ecm_certificate_path = value.strip()

    def get_ecm_certificate_path(self):
        return self.__ecm_certificate_path

    def set_ecm_certificate_bkp_path(self, value):
        self.__ecm_certificate_bkp_path = value.strip()

    def get_ecm_certificate_bkp_path(self):
        return self.__ecm_certificate_bkp_path

    def set_ecm_namespace(self, value):
        self.__ecm_namespace = value.strip()

    def get_ecm_namespace(self):
        return self.__ecm_namespace