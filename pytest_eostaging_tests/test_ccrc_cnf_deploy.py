
from com_ericsson_do_auto_integration_scripts.CCRC_CNF_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_create_vnf_identifier():
    """
    This test method is used to Create VNF Identifier
    """
    create_ccrc_vnf_identifier()



def test_upload_ccrc_ccd_target_cnfig():
    """
    This test method is used to Upload the target CCD config
    """
    upload_ccrc_ccd_target_cnfig()



def test_ccrc_instantiate_cnf():
    """
    This test method is used to Instantiate the CNF
    """
    ccrc_instantiate_cnf()



def test_ccrc_verify_cnf():
    """
    This test method is used to Verify CNF Instantiation
    """
    ccrc_verify_cnf()
