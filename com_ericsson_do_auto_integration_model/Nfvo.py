'''
Created on 15 Aug 2018

@author: emaidns
'''



class Nfvo(object):
    
    
    def get_orvnfm_version(self):
        return self.__orvnfm_version

    def set_orvnfm_version(self, value):
        self.__orvnfm_version = value
    
    def get_core_vm_ip(self):
        return self.__CORE_VM_IP


    def set_core_vm_ip(self, value):
        self.__CORE_VM_IP = value.strip()

    def get_core_vm_hostname(self):
        return self.__CORE_VM_HOSTNAME

    def set_core_vm_hostname(self, value):
        self.__CORE_VM_HOSTNAME = value.strip()

    def get_isNfvoAvailable(self):
        return self.__isNfvoAvailable
    
    def get_isGrantSupported(self):
        return self.__isGrantSupported

    def get_grantUrl(self):
        return self.__grantUrl
    
    def get_username(self):
        return self.__username
    
    def get_password(self):
        return self.__password
    
    def get_subscriptionId(self):
        return self.__subscriptionId
    
    def get_tenantid(self):
        return self.__tenantid
    
    def get_vdcId(self):
        return self.__vdcId
    
    def get_nfvoAuthUrl(self):
        return self.__nfvoAuthUrl
    
    def get_enmHostName(self):
        return self.__enmHostName

    
    
    def set_isNfvoAvailable(self, value):
        self.__isNfvoAvailable = value

    def set_isGrantSupported(self,value):
        self.__isGrantSupported = value
        
    def set_grantUrl(self, value):
        self.__grantUrl = value


    def set_username(self, value):
        self.__username = value.strip()


    def set_password(self, value):
        self.__password = value.strip()


    def set_subscriptionId(self, value):
        self.__subscriptionId = value


    def set_tenantid(self, value):
        self.__tenantid = value
        
    def set_vdcId(self, value):
        self.__vdcId = value


    def set_nfvoAuthUrl(self, value):
        self.__nfvoAuthUrl = value
        
    def set_enmHostName(self, value):
        self.__enmHostName = value



 
    def __getattribute__(self, *args, **kwargs):
        return object.__getattribute__(self, *args, **kwargs)

    def get_json_file_data(self):
        self.json_file_data = {

            "baseUrl": self.get_nfvoAuthUrl(self),
            "hostName": self.get_core_vm_hostname(self),
            "hostIpAddress": self.get_core_vm_ip(self),
            "userName": self.get_username(self),
            "password": self.get_password(self),
            "enmHostName": self.get_enmHostName(self),
            "authType": "Basic",
            "subscriptionId": self.get_subscriptionId(self),
            "isGrantSupported": self.get_isGrantSupported(self),
            "isNotificationSupported": "true",
            "nfvoType": "ECM",
            "nfvoInUse": "Y",
            "tenancyDetails": [{
                "tenantId": self.get_tenantid(self),
                "tenantName": "",
                "defaultTenant": "true",
                "vdcDetails": [{
                    "id": self.get_vdcId(self),
                    "name": "",
                    "defaultVdc": "true"
                }]
            }],
            "nfvoEndPoints": [{
                "endPointName": "grantUrl",
                "endPointUrl": "/grant/v1/grants"
            },
            {
                "endPointName": "authUrl",
                "endPointUrl": "/tokens"
            },
            {
                "endPointName": "lifecycleNotificationUrl",
                "endPointUrl": "/VnfLcmOperationOccurrenceNotification"
            },
            {
                "endPointName": "createNotificationUrl",
                "endPointUrl": "/vnf/v1/vnf_instances/creation"
            },
            {
                "endPointName": "deleteNotificationUrl",
                "endPointUrl": "/vnf/v1/vnf_instances/deletion"
            },
            {
                "endPointName": "packageManagementUrl",
                "endPointUrl": "/vnfpkgm/v1/vnf_packages"
            }
            ],
            "nfvoProperties": [{
                "propKey": "nfvoSupportedNotificationTypes",
                "propValue": "CREATE, DELETE, START, PROCESSING, ROLLED_BACK, COMPLETED, FAILED"
            }]
              
        }

        return self.json_file_data
    
    
    def set_json_file_data(self,value):
        self.json_file_data = value
    