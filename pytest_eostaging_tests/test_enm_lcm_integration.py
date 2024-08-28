

from com_ericsson_do_auto_integration_scripts.ENM_LCM_INTEGRATION import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_enm_lcm_integration():
    """
    This test method is used  to integrate ENM LCM
    """
    enm_lcm_integration()
    

    

