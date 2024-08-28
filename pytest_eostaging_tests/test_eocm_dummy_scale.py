
from com_ericsson_do_auto_integration_scripts.EOCM_DUMMY_SCALE import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_eocm_scaleout():
    """
    This test method is used  to scale out dummy vnf type.
    """    
    eocm_scaleout()
    

def test_eocm_scalein():
    """
    This test method is used  to scale in dummy vnf type.
    """    
    eocm_scalein()
  

def test_verify_dummy_workflow():
    """
    This test method is used  to verify dummy workflow version.
    """    
    verify_eocm_dummy_scale_workflow_version()




