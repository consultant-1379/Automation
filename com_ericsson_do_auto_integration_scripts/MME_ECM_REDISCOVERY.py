from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger

from com_ericsson_do_auto_integration_scripts.ECM_NODE_REDISCOVERY import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *


log = Logger.get_logger('MME_ECM_REDISCOVERY.py')

def MME_discovery_workflow_deployment():
    discovery_workflow_deployment('MME')


def delete_MME_vapp_entry_cmdb():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    global MME_vapp_name
    MME_vapp_name = sit_data._SIT__mme_package_name

    global vdcname
    global vdc_id

    vdcname,vdc_id = fetch_vdc_name_id_EOCM(MME_vapp_name,'MME')

    delete_vapp_entry_cmdb(MME_vapp_name,vdcname)

def delete_MME_vapp_vnflcmdb():
    delete_vapp_vnflcmdb(MME_vapp_name)


def MME_list_discovery():
    list_discovery(MME_vapp_name)

def MME_discover_vapp():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    
    default_vdc_id = sit_data._SIT__vdc_id
    vnfm_id = sit_data._SIT__vnfManagers
    vnf_packageid = sit_data._SIT__mme_packageId
    vimzone_name = sit_data._SIT__vimzone_name
    discover_vapp(MME_vapp_name, vnfm_id, MME_vapp_name, default_vdc_id, vnf_packageid, vimzone_name)


def MME_discover_workflow_status():
    node_defination_name = 'Discover VNF v1'
    check_lcm_workflow_status(MME_vapp_name,node_defination_name)
