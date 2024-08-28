
from com_ericsson_do_auto_integration_scripts.UDS_POST_INSTALL import UDC_POST_INST as uds_post_inst
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_uds_backup():
    """
    This test method is used to take backup of uds
    """
    uds_post_inst.take_backup_of_uds(uds_post_inst)


