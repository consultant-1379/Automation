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
# pylint: disable=C0302,C0103,C0114,C0116,W0703,W0212,R1705,R0914,W0612,R1702,R0912,R0915
# pylint: disable=C0209, C0301
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECM_NODE_REDISCOVERY import discovery_workflow_deployment, \
    delete_vapp_vnflcmdb, list_discovery, discover_vapp, delete_vapp_from_cmdb_ecm, delete_vapp_entry_cmdb
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import check_lcm_workflow_status
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_vapp_cmdb_del_file

log = Logger.get_logger('EPG_ECM_REDISCOVERY.py')
epg_vapp_name = None


def epg_discovery_workflow_deployment():
    discovery_workflow_deployment('TOSCA-EPG')


def delete_epg_vapp_entry_cmdb():
    global epg_vapp_name
    epg_vapp_name = SIT.get_tosca_epg_vapp(SIT)
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        file_name = "cmdb_vapp_delete.json"
        update_vapp_cmdb_del_file(file_name, epg_vapp_name)
        delete_vapp_from_cmdb_ecm("TOSCA-EPG", file_name)
    else:
        vdc_name = SIT.get_vdc_name(SIT)
        delete_vapp_entry_cmdb(epg_vapp_name, vdc_name)


def delete_epg_vapp_vnflcmdb():
    delete_vapp_vnflcmdb(epg_vapp_name)


def epg_list_discovery():
    list_discovery(epg_vapp_name)


def epg_discover_vapp():
    vnfm_id = SIT.get_vnf_managers(SIT)
    vnf_packageid = SIT.get_vnf_packageId(SIT)
    vimzone_name = SIT.get_vimzone_name(SIT)
    # while deleting Service / vapp as part of pipeline getting error sometimes that the vdc is in use already
    # and cant delete the service,so thats why replacing the vdc_id to default_vdc_id
    default_vdc_id = SIT.get_vdc_id(SIT)
    discover_vapp(epg_vapp_name, vnfm_id, epg_vapp_name, default_vdc_id, vnf_packageid, vimzone_name)


def epg_discover_workflow_status():
    node_defination_name = 'Discover VNF v1'
    check_lcm_workflow_status(epg_vapp_name, node_defination_name)
