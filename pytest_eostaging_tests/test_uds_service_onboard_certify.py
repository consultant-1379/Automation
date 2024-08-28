from com_ericsson_do_auto_integration_scripts.UDS_SERVICE_OPERATIONS import UDS_SERVICE as uds_service
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_create_uds_service():
    """
    This test method is used to Create Service in UDS
    """
    uds_service.create_uds_service(uds_service)
    

def test_add_vf_to_service(): 
    """
    This test method is used to Add VF to Service
    """   
    uds_service.add_vf_to_the_service(uds_service)


def test_certify_the_service():    
    """
    This test method is used to Certify the Service
    """
    uds_service.certify_the_service(uds_service)
    

def test_distribute_the_service():
    """
    This test method is used to Distribute the Service to SO
    """    
    uds_service.distribute_the_service(uds_service)

def test_verify_onboarded_service_template():    
    """
    This test method is used to Verify Service template on-boarded to SO
    """
    fetch_service_modelId_uds_so_template("EPG")

