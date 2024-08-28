
from com_ericsson_do_auto_integration_scripts.CCRC_CNF_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_get_aspect_id_for_scale():
    """
    This test method is used to Get Aspect id for scale
    """
    get_aspect_id_for_scale()



def test_scale_out_ccrc_cnf():
    """
    This test method is used to Scale out CCRC CNF
    """
    scale_out_ccrc_cnf()



def test_verify_ccrc_cnf_scale_out():
    """
    This test method is used to Verify Scale out CCRC CNF
    """
    verify_ccrc_cnf_scale_out()



def test_scale_in_ccrc_cnf():
    """
    This test method is used to Scale in CCRC CNF
    """
    scale_in_ccrc_cnf()


def test_verify_ccrc_cnf_scale_in():
    """
    This test method is used to Verify Scale in CCRC CNF 
    """
    verify_ccrc_cnf_scale_in()

