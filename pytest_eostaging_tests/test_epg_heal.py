from start_script import *
from com_ericsson_do_auto_integration_scripts.EPG_SCALE_HEAL import EPG_SCALE_OPERATIONS as epg_scale_ope


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_epg_heal():
    """
    This test method is used  to perform heal on EPG vnf type.
    """
 
    epg_scale_ope.epg_heal(epg_scale_ope)
    
    
