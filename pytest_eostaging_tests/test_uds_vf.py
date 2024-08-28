

from com_ericsson_do_auto_integration_scripts.UDS_VF_OPERATIONS import UDS_VF as uds_vf
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_create_vf():
    """
    This test method is used  to Create vf to UDS
    """
    uds_vf.create_vf(uds_vf)
    


def test_add_epg_vfc_to_vf():    
    """
    This test method is used  to Add EPG vfc to vf composition
    """
    uds_vf.add_epg_vfc_to_vf_composition(uds_vf)



def test_add_network_service():    
    """
    This test method is used  to Add network_service vfc to vf composition
    """
    uds_vf.add_network_service_vfc_to_vf_composition(uds_vf)
    


def test_associate_epg_to_network_service():    
    """
    This test method is used  to Associate epg to network service
    """
    uds_vf.associate_epg_to_network_service(uds_vf)
    



def test_onboard_ecm_request_template():    
    """
    This test method is used  to Onboard the ECM request template
    """
    uds_vf.onboard_the_ecmrequest_template(uds_vf)
    


def test_onboard_day1_config():    
    """
    This test method is used  to Onboard the day1config template
    """
    uds_vf.onboard_the_day1config_template(uds_vf)
    

    

def test_create_epg_inputs():    
    """
    This test method is used  to Create EPG inputs
    """
    uds_vf.create_epg_inputs(uds_vf)
    


def test_create_ns_inputs(context):    
    """
    This test method is used  to Create Network Service inputs
    """
    uds_vf.create_ns_inputs(uds_vf)
    


def test_add_epg_properties():    
    """
    This test method is used  to  Add EPG properties
    """
    uds_vf.add_epg_properties(uds_vf)




def test_add_ns_properties():    
    """
    This test method is used  to Add Network Service properties
    """
    uds_vf.add_ns_properties(uds_vf)



def test_certify_created_vf():    
    """
    This test method is used  to Certify created VF
    """
    uds_vf.certify_created_vf(uds_vf)
