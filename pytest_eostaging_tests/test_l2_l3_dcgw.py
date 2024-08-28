
from com_ericsson_do_auto_integration_scripts.L2_L3_DCGW import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_create_dcgw():
    """
    This test method is used to create DC-GW in EO-CM.
    """
    create_dcgw_eo_cm()


def test_verify_dcgw_creation():
    """
    This test method is used to verify Creation of DC-GW in EO-CM.
    """
    
    verify_l2_l3_dcgw_creation()



def test_create_vrf_dcgw():
    """
    This test method is used to create vrf DC-GW in EO-CM.
    """
    create_vrf_dcgw()

