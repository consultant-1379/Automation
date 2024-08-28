'''
Created on 20 Aug 2018

@author: eiaavij
'''

import random

class Ecm(object):
    
   

    def get_name(self):
        return self.__name

    def get_type(self):
        return self.__type

    def get_default_vim(self):
        return self.__default_Vim


    def get_host_ip_address(self):
        return self.__host_ip_address


    def get_host_name(self):
        return self.__host_name


    def get_auth_url(self):
        return self.__auth_url


    def get_tenants(self):
        return self.__tenants


    def set_name(self, value):
        self.__name = value +'_'+ str(random.randint(0,999))

    
    def set_type(self,value):
        self.__type = value
    
    def set_default_vim(self, value):
        self.__default_Vim = value


    def set_host_ip_address(self, value):
        self.__host_ip_address = value.strip()


    def set_host_name(self, value):
        self.__host_name = value.strip()


    def set_auth_url(self, value):
        self.__auth_url = value


    def set_tenants(self, value):
        self.__tenants = value
        
        
    def __getattribute__(self, *args, **kwargs):
        return object.__getattribute__(self, *args, **kwargs)

    def get_json_file_data(self):
        self.json_file_data = {
                "name": self.get_name(self),
                "type": self.get_type(self),
                "defaultVim": self.get_default_vim(self) ,
                "hostIpAddress": self.get_host_ip_address(self), 
                "hostName": self.get_host_name(self), 
                "authUrl": self.get_auth_url(self),
                "tenants":self.get_tenants(self)
        }
        
        return self.json_file_data
    
    
    def set_json_file_data(self,value):
        self.json_file_data = value    