

'''
Created on 10 sep 2018

@author: eshetra

'''



class Ecm_PI(object):    
    
    def get_allocation_pools_ip(self):
        return self.__allocation_pools_ip

    def set_allocation_pools_ip(self, value):
        self.__allocation_pools_ip = value.strip()

    def get_rdb_vm_ip(self):
        return self.__RDB_VM_IP
    
    def get_rdb_vm_username(self):
        return self.__RDB_VM_USERNAME
    
    def get_rdb_vm_password(self):
        return self.__RDB_VM_PASSWORD
    

    def set_rdb_vm_ip(self, value):
        self.__RDB_VM_IP = value.strip()


    def set_rdb_vm_username(self, value):
        self.__RDB_VM_USERNAME = value.strip()


    def set_rdb_vm_password(self, value):
        self.__RDB_VM_PASSWORD = value.strip()
    
    
    def get_activation_gui_username(self):
        return self.__activation_gui_username


    def get_activation_gui_password(self):
        return self.__activation_gui_password
    
    def set_activation_gui_username(self, value):
        self.__activation_gui_username = value.strip()

    def set_activation_gui_password(self, value):
        self.__activation_gui_password = value.strip() 
    
    def get_deployment_type(self):
        return self.__deployment_type
    
    def set_deployment_type(self, value):
        self.__deployment_type = value.strip()
        
    # Below is used for site creation login in case of HA deployment in ECM_POST_INSTALLATION.py
    def get_core_vm_ha_vm_ip(self):
        return self.__CORE_VM_HA_IP
    
    def set_core_vm_ha_ip(self, value):
        self.__CORE_VM_HA_IP = value.strip()

    def get_core_vm_2_ha_vm_ip(self):
        return self.__CORE_VM_2_HA_IP

    def set_core_vm_2_ha_ip(self, value):
        self.__CORE_VM_2_HA_IP = value.strip()
    
    def get_vcisco_management_ip(self):
        return self.__vCisco_Management_ip


    def get_vcisco_management_username(self):
        return self.__vCisco_Management_username


    def get_vcisco_management_password(self):
        return self.__vCisco_Management_Password


    def get_activation_vm_ip(self):
        return self.__activation_vm_ip
    
    def get_asr_device_name(self):
        return self.__asr_device_name  
    
    def set_asr_device_name(self, value):
        self.__asr_device_name = value.strip()  
        
    def get_dcgw_ne_name(self):
        return self.__dcgw_ne_name
    
    def set_dcgw_ne_name(self, value):
        self.__dcgw_ne_name = value.strip()

    def get_vm_deployment_name(self):
        return self.__vm_deployment_name

    def set_vm_deployment_name(self, value):
        self.__vm_deployment_name = value.strip()
     

    def get_activation_vm_username(self):
        return self.__activation_vm_username


    def get_activation_vm_password(self):
        return self.__activation_vm_password      
        

    def set_activation_vm_ip(self, value):
        self.__activation_vm_ip = value.strip()


    def set_activation_vm_username(self, value):
        self.__activation_vm_username = value.strip()


    def set_activation_vm_password(self, value):
        self.__activation_vm_password = value.strip()  
    
    
    def set_vcisco_management_ip(self, value):
        self.__vCisco_Management_ip = value.strip()


    def set_vcisco_management_username(self, value):
        self.__vCisco_Management_username = value.strip()


    def set_vcisco_management_password(self, value):
        self.__vCisco_Management_Password = value.strip()
        
    
    def get_ecm_host_name(self):
        return self.__ECM_Host_Name
    
    def get_ecm_host_blade_ip(self):
        return self.__ECM_Host_Blade_IP


    def get_ecm_host_blade_username(self):
        return self.__ECM_Host_Blade_username


    def get_ecm_host_blade_password(self):
        return self.__ECM_Host_Blade_Password

     
    def get_core_vm_ip(self):
        return self.__CORE_VM_IP
    
    def get_core_vm_username(self):
        return self.__CORE_VM_USERNAME
    
    def get_core_vm_password(self):
        return self.__CORE_VM_PASSWORD
    

    def set_core_vm_ip(self, value):
        self.__CORE_VM_IP = value.strip()


    def set_core_vm_username(self, value):
        self.__CORE_VM_USERNAME = value.strip()
        
    def get_core_vm_hostname(self):
        return self.__core_vm_hostname
    
    def set_core_vm_hostname(self, value):
        self.__core_vm_hostname = value.strip()


    def set_core_vm_password(self, value):
        self.__CORE_VM_PASSWORD = value.strip()
    
    def set_ecm_host_name(self, value):
        self.__ECM_Host_Name = value.strip()
        
    def set_ecm_host_blade_ip(self, value):
        self.__ECM_Host_Blade_IP = value.strip()


    def set_ecm_host_blade_username(self, value):
        self.__ECM_Host_Blade_username = value.strip()


    def set_ecm_host_blade_password(self, value):
        self.__ECM_Host_Blade_Password = value.strip()
        
