
from com_ericsson_do_auto_integration_scripts.ETSI_DUMMY_TOSCA_SCALEHEAL import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_etsi_dummy_tosca_scale_out():
    """
    This test method is used  to ETSI Dummy Tosca Deployment Scale out
    """
    etsi_dummy_tosca_depl_scaleout()
    

def test_etsi_dummy_tosca_scale_in():
    """
    This test method is used  to ETSI Dummy Tosca Deployment Scale in
    """
    etsi_dummy_tosca_depl_scalein()



def test_dummy_tosca_heal():
    """
    This test method is used  to ETSI Dummy Tosca Deployment Scale Heal
    """
    etsi_dummy_tosca_depl_heal()
        

def test_verify_dummy_tosca_heal():
    """
    This test method is used  to check workflow version of ETSI Dummy Tosca Scale operations
    """
    verify_etsi_tosca_dummyheal_workflow_verison()
