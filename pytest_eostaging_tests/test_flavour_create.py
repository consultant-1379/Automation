from com_ericsson_do_auto_integration_scripts.ECM_RANDOM_OPERATIONS import *
from start_script import *


def test_collect_user_input_DIT(DIT_name,vnf_type):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, vnf_type, 'False')



def test_create_flavour():
    """
    This test method is used to create flavour"
    """
    start_flavour_creation()


