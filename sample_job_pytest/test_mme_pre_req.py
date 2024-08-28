from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_mme_remove_lcm_entry():
    """
    This test method is used to remove the old LCM entry in mme usecase.
    """
    remove_LCM_entry()



def test_mme_admin_heatstack_rights():
    """
    This test method is used to give heatstack rights to user in mme usecase.
    """
    admin_heatstack_rights()


