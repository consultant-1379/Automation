
from com_ericsson_do_auto_integration_scripts.ECDE_SPINNAKER_CLEANUP import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')




def test_token_for_admin():
    """
    This test method is used to Extract token for admin
    """
    
    extract_token_for_admin()



def test_token_for_spinnaker():
    """
    This test method is used  to fetch and delete the pipeline
    """
    extract_access_token_for_spinnaker()


