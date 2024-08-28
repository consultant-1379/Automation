'''
Created on 22 Aug 2018

@author: eiaavij
'''

#Inputs of RegisterVnfm.json

registervnfm_description = "VNFM LCM endpoint info Authentication"
registervnfm_type = "EXTERNAL_V2"
registervnfm_vendor = "Ericsson"
registervnfm_siteName = "Athlone Data Center"
registervnfm_vnfmType = "EXTERNAL_V2"
registervnfm_endpoints_name = "vnfmEndpoint"
registervnfm_endpoints_port = "443"
registervnfm_endpoints_testUri = "/vnflcm"
registervnfm_defaultSecurityConfig_securtiyType = "HTTPS"
registervnfm_authPort = "443"
registervnfm_authpath = "/login"
registervnfm_authtype = "ENM"

#Inputs of NfvoConfig.json

nfvoconfig_isNfoAvailable = "True"
nfvoconfig_isGrantSupported = "True"
nfvoconfig_tenanid = "ECM"

# Inputs of Cee_template.json 

cee_type = "CEE"
cee_defaultVim = "True"
cee_tenants_defaultTenant = "True"

# Inputs of Atlas_template.json

atlas_name = "atlas_vim"
atlas_type = "CEE"
atlas_dafaultVim = "False"
atlas_tenants_defaultTenant = "True"

# Inputs of Ecm_template.json

ecm_name = "ecm_vim"
ecm_type = "ECM"
ecm_defaultVim = "False"
ecm_tenants_name = "ECM"
ecm_tenants_id = "ECM_id"
ecm_tenants_defaultTenant = "True"

# folder names

int_files = 'com_ericsson_do_auto_integration_files'
