from com_ericsson_do_auto_integration_scripts.EPG_ECM_REDISCOVERY import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_epg_discovery_workflow_deployment():
    """
    This test method is used to nstall VNFLCM discovery workflow for EPG
    """
    epg_discovery_workflow_deployment()


def test_delete_epg_vapp_entry_cmdb():
    """
    This test method is used to Delete the EPG vapp entry from cmdb in ECM
    """
    delete_epg_vapp_entry_cmdb()


def test_delete_epg_vapp_vnflcmdb():
    """
    This test method is used to Delete the EPG vapp entry from VNFLCM DB
    """
    delete_epg_vapp_vnflcmdb()


def test_epg_list_discovery():
    """
    This test method is used to Query- API to see the list of Discovery For EPG
    """
    epg_list_discovery()


def test_epg_discover_vapp():
    """
    This test method is used to Discover vapp and ECM Order status check
    """
    epg_discover_vapp()


def test_epg_discover_workflow_status():
    """
    This test method is used to LCM workflow verification for Discovered EPG
    """
    epg_discover_workflow_status()