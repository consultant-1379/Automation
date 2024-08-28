
from com_ericsson_do_auto_integration_scripts.CCRC_CNF_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_onboard_ccrc_vnf():
    """
    This test method is used  to Create VNF Package Resource ID
    """
    onboard_ccrc_vnf_package()


def test_onboard_ccrc_cnf():
    """
    This test method is used  to Create VNFD ID
    """
    onboard_ccrc_cnf_package()


def test_verify_ccrc_cnf_onboard():
    """
    This test method is used  to verify the CCRC CSAR Package
    """
    verify_ccrc_cnf_onboarding()
