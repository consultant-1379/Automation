

from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_EVNFM_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_create_dummy_node_vnf_type():
    """
    This test method is used to create VNF-TYPE FOR DUMMY NODE
    """
    create_dummy_node_vnf_type()


def test_create_dummy_node_validation_level():
    """
    This test method is used to create validation levels for DUMMY NODE
    """
    create_dummy_node_validation_level()



def test_create_EVNFM_validation_profile():
    """
    This test method is used to create validation stream for EVNFM
    """
    create_EVNFM_validation_profile()



def test_create_EVNFM_onboarding_system():
    """
    This test method is used to create Onboarding System for EVNFM
    """
    create_EVNFM_onboarding_system()



def test_create_EVNFM_test_env_profile():
    """
    This test method is used to create Test Environment profile for EVNFM
    """
    create_EVNFM_test_env_profile()



def test_create_EVNFM_validation_track():
    """
    This test method is used to create a Vendor-Specific Validation Tracks for EVNFM
    """
    create_EVNFM_validation_track()


def test_assign_EVNFM_validation_track():
    """
    This test method is used to assign Vendor-Specific Validation Tracks to EVNFM TEP
    """
    assign_EVNFM_validation_track()




