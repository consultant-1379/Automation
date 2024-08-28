'''
Created on 15 Aug 2018

@author: emaidns
'''

import random

class Vnfm(object):
    
    
    def get_sol_version(self):
        return self.__sol_version

    def set_sol_version(self, value):
        self.__sol_version = value
    
    
    def get_enm_ipaddress(self):
        return self.__enm_ipaddress

    def set_enm_ipaddress(self, value):
        self.__enm_ipaddress = value.strip()

    def get_name(self):
        return self.__name
    
    def get_description(self):
        return self.__description

    def get_type(self):
        return self.__type
    
    def get_vendor(self):
        return self.__vendor
    
    def get_siteName(self):
        return self.__siteName
    
    def get_vnfmType(self):
        return self.__vnfmType
    
    def get_endpoints(self):
        return self.__endpoints
    
    def get_defaultSecurityConfig(self):
        return self.__defaultSecurityConfig
    

    
    def get_authIpAddress(self):
        return self.__authIpAddress
    
    def get_authPort(self):
        return self.__authPort
    
    def get_authPath(self):
        return self.__authPath
    
    def get_authUserName(self):
        return self.__authUserName
    
    def get_authPassword(self):
        return self.__authPassword
    
    def get_authType(self):
        return self.__authType
    
    def set_name(self, value):
        self.__name = value +'_'+ str(random.randint(0,999))

    def set_description(self,value):
        self.__description = value
        
    def set_type(self, value):
        self.__type = value


    def set_vendor(self, value):
        self.__vendor = value


    def set_siteName(self, value):
        self.__siteName = value


    def set_vnfmType(self, value):
        self.__vnfmType = value


    def set_endpoints(self, value):
        self.__endpoints = value
        
    def set_defaultSecurityConfig(self, value):
        self.__defaultSecurityConfig = value



        
    def set_authIpAddress(self, value):
        self.__authIpAddress = value.strip()

    def set_authPort(self, value):
        self.__authPort = value.strip()
        
    def set_authPath(self, value):
        self.__authPath = value.strip()

    def set_authUserName(self, value):
        self.__authUserName = value.strip()
        
    def set_authPassword(self, value):
        self.__authPassword = value.strip()

    def set_authType(self, value):
        self.__authType = value.strip()

    
    def __getattribute__(self, *args, **kwargs):
        return object.__getattribute__(self, *args, **kwargs)

    def get_json_file_data(self):
        self.json_file_data = {
                "name": self.get_name(self),
                "description": self.get_description(self),
                "type": self.get_type(self),
                "vendor": self.get_vendor(self),
                "siteName": self.get_siteName(self),
                "vnfmType": self.get_vnfmType(self),
                "endpoints": self.get_endpoints(self),
                "defaultSecurityConfig": self.get_defaultSecurityConfig(self),
                "authIpAddress": self.get_authIpAddress(self), 
                "authPort": self.get_authPort(self), 
                "authPath": self.get_authPath(self),
                "authUserName":self.get_authUserName(self),
                "authPassword": self.get_authPassword(self),
                "authType":self.get_authType(self),
                "sol003Version":self.get_sol_version(self),
                "vnfmPlacementSupport":"standardsCompliant",
                "discoverySupported":"true"
        }
        
        return self.json_file_data
    
    
    def set_json_file_data(self,value):
        self.json_file_data = value
    