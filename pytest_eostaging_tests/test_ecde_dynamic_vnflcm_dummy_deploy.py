from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_VNFLCM_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_transfer_vnflaf_dir_to_vnflcm():
    """
    This test method is used to Transfer vnf package to VNFLCM
    """
    transfer_vnflaf_dir_to_vnflcm()
    
def test_remove_nfvo_if_exist():
    """
    This test method is used to Remove NFVO if exists in VNF-LCM
    """
    check_VNFLCM_remove_nfvo()
    
def test_install_vnflcm_dummy_workflow():
    """
    This test method is used to Install Dummy VNF workflow in VNF-LCM
    """
    install_VNFLCM_dummy_workflow()

def test_create_vnflcm_dummy_product():
    """
    This test method is used to Create Vendor_Product For Dummy Node ECDE-VNFLCM
    """
    create_VNFLCM_dummy_product()
    
def test_upload_vnflcm_image_resource():
    """
    This test method is used to Upload Image Resource to Vendor_Product ECDE-VNFLCM
    """
    upload_VNFLCM_image_resource() 

def test_upload_vnflcm_wrapper_resource():
    """
    This test method is used to Upload Wrapper file Resource to Vendor_Product ECDE-VNFLCM"
    """
    upload_VNFLCM_wrapper_resource()
    
def test_get_level_and_stream_id_of_validation():
    """
    This test method is used to Get Validation level and Validation stream Id to Validate Product ECDE-VNFLCM
    """
    get_VNFLCM_val_stream_val_level_id()
    
def test_validate_vnflcm_dummy_vendor_product():
    """
    This test method is used to Validate Vendor_Product ECDE-VNFLCM
    """
    validate_VNFLCM_dummy_vendor_product() 
    
def test_verify_vnflcm_dummy_validation_order():
    """
    This test method is used to Verification of Validation order ECDE-VNFLCM
    """
    verify_VNFLCM_dummy_validation_order()    
    
