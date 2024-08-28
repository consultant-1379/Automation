from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
import random

log = Logger.get_logger('EPG_ETSI_TOSCA_NSD_PREREQUISITE.py')

def remove_LCM_entry_epg_etsi():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if 'FALSE' == is_vm_vnfm:
        remove_host_lcm_entry()

def admin_heatstack_rights_epg_etsi():
    
    update_admin_heatstack_rights()
    
def update_lcm_password_epg_etsi():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if 'FALSE' == is_vm_vnfm:
        update_lcm_oss_password()


def transfer_epg_etsi_tosca_nsd_software():
    
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_etsi_tosca_nsd_software_path = sit_data._SIT__epgEtsiNsdSoftwarePath
    epg_etsi_tosca_nsd_version = sit_data._SIT__epgEtsiNsdVersion
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm
    
    if epg_etsi_tosca_nsd_version == 'EPG3.7':
        
        hot_file = 'vEPG3.hot.yaml'
    
    else:
        
        hot_file = 'template.yaml'
    
    if 'TRUE' == is_vm_vnfm: 
    
        transfer_node_software_vm_vnfm('EPG_ETSI_TOSCA_NSD',epg_etsi_tosca_nsd_software_path,epg_etsi_tosca_nsd_version)

    else:
        
        transfer_node_software('EPG_ETSI_TOSCA_NSD',epg_etsi_tosca_nsd_software_path,epg_etsi_tosca_nsd_version,hot_file)

def unpack_epg_etsi_software():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm

    if 'FALSE' == is_vm_vnfm:
        epg_etsi_tosca_nsd_version = sit_data._SIT__epgEtsiNsdVersion
        if epg_etsi_tosca_nsd_version == 'EPG3.7':
        
            hot_file = 'vEPG3.hot.yaml'
    
        else:
        
            hot_file = 'template.yaml'
        
        unpack_node_software('EPG_ETSI_TOSCA_NSD', epg_etsi_tosca_nsd_version, 'EPG_Software_complete.tar', 'EPG_Software_resources.tar', hot_file)

def epg_etsi_nsd_workflow_deployment():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    epg_etsi_tosca_nsd_version = sit_data._SIT__epgEtsiNsdVersion

    epg_etsi_tosca_nsd_software_path = r'/vnflcm-ext/current/vnf_package_repo/'+epg_etsi_tosca_nsd_version
    is_vm_vnfm = sit_data._SIT__is_vm_vnfm
    
    if 'TRUE' == is_vm_vnfm:
        epg_workflow_deployment_vm_vnfm(epg_etsi_tosca_nsd_software_path)
    else:
        epg_workflow_deployment(epg_etsi_tosca_nsd_software_path)
    
    

def generate_ssh_key_epg_etsi():
    ssh_key_generate_on_lcm()


def create_epg_etsi_flavours():
    create_epg_flavours()

def register_epg_etsi_images():
    register_epg_images()


