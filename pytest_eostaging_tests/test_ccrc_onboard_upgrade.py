
from com_ericsson_do_auto_integration_scripts.CCRC_CNF_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_onboard_ccrc_vnf_pacakge():
    """
    This test method is used to Create VNF Package Resource ID upgrade
    """
    onboard_ccrc_vnf_package()


def test_onboard_ccrc_cnf_package():
    """
    This test method is used to Onboard the CCRC CSAR Package to Upgrade
    """
    onboard_ccrc_cnf_package(upgrade = True)


def test_verify_ccrc_cnf_onboard():
    """
    This test method is used to Verify the Upgrade CCRC CSAR Package
    """
    verify_ccrc_cnf_onboarding(upgrade = True)

