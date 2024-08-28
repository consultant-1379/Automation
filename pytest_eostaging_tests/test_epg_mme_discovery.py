from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.EPG_MME_DISCOVERY import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_delete_epg_and_mme_record_from_cmdb():
    """
    This test is used to delete the epg and mme records from cmdb before starting discovery test
    """
    delete_epg_and_mme_record_from_cmdb()



def test_vdc_creation():
    """
    This test is used to create virtual data center for discovery test
    """
    vdc_creation()



def test_discovery_of_epg_and_mme():
    """
    This test is used to discover the epg and mme
    """
    discovery_of_epg_and_mme()
