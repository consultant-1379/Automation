
from com_ericsson_do_auto_integration_scripts.UDS_POST_INSTALL import UDC_POST_INST as uds_post_inst
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_uds_cleanup():
    """
    This test method is used to Clean up UDS data
    """
 
    uds_post_inst.cleanup_data_on_uds(uds_post_inst)


def test_restart_uds():
    """
    This test method is used to Restart the POD and wait for it to be running
    """
 
    uds_post_inst.restart_uds_service_pod(uds_post_inst)