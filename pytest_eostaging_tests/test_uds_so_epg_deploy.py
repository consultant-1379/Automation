from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_update_onboard_file():
    """
    This test method is used to to Update Onboard file for EPG package onboarding.
    """
    update_onboard_file()




def test_onboard_epg_package():
    """
    This test method is used to Start onboarding the EPG package
    """
    onboard_epg_package()



def test_verify_epg_package():
    """
    This test method is used to Verify onboarded EPG package
    """
    verify_epg_package()


def test_fetch_node_nsd_package():
    """
    This test method is used to Fetch NSD package from ECM to prepare ns1.yaml file
    """
    fetch_node_nsd_package()


def test_update_node_nsd_template():
    """
    This test method is used to Update NSD package and CSAR it
    """
    update_node_nsd_template()


def test_onboard_node_subsytems():
    """
    This test method is used  to Onboard the ECM and ENM subsystems to SO
    """
    onboard_node_subsytems()


def test_onboard_node_nsd_template():
    """
    This test method is used  to Start onboarding the NSD package
    """
    onboard_node_nsd_template()


def test_fetch_service_model_id_uds():
    """
    This test method is used to Fetch out the service model Id , needed in case of UDS
    """
    fetch_service_model_id_uds()



def test_create_epg_uds_so_network_service():
    """
    This test method is used to Create Network Service for EPG deployment using UDS
    """
    create_epg_uds_so_network_service()



def test_verify_node_service_status():
    """
    First step verification
    This test method is used to polling the state of network service using service ID for deployed node
    """
    verify_node_service_status()



def test_check_epg_lcm_workflow_status():
    """
    Second step verification
    This test method is used to of checking LCM workflow for EPG VNF in VNFLCM/VMVNFM.
    """
    check_epg_lcm_workflow_status()


def test_check_epg_ecm_order():
    """
    Third step verification
    This test method is used for checking ECM order status for EPG
    """
    check_epg_ecm_order()


def test_check_epg_ip_ping_status():
    """
    Fourth step verification
    This test method is used for pinging the deployed Node for EPG
    """
    check_epg_ip_ping_status()


def test_check_epg_bulk_configuration():
    """
    Fifth Step verification
    This test method is used to checking bulk configuration
    """
    check_epg_bulk_configuration()

