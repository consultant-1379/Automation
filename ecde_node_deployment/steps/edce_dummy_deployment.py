'''
Created on Oct 18, 2019

@author: emaidns
'''
from behave import *
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_VNFLCM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_EVNFM_DEPLOYMENT import *

@step("I start the Scenario to Create Vendor_Product For Dummy Node ECDE-ECM")
def step_impl(context):
    create_ECM_dummy_product()


@step("I start the Scenario to Upload Image Resource to Vendor_Product ECDE-ECM")
def step_impl(context):
    upload_ECM_image_resource() 


@step("I start the Scenario to Upload Template Resource to Vendor_Product ECDE-ECM")
def step_impl(context):
    upload_ECM_hotfile_resource()
    
    
    
@step("I start the Scenario to Get Validation level and Validation stream Id to Validate Product ECDE-ECM")
def step_impl(context):
    get_ECM_val_stream_val_level_id()
    
    

@step("I start the Scenario to Validate Vendor_Product ECDE-ECM")
def step_impl(context):
    validate_ECM_dummy_vendor_product()
    
    
    
@step("I start the Scenario to Verification of Validation order ECDE-ECM")
def step_impl(context):
    verify_ECM_dummy_validation_order()
    
    

##########################################################################################################################

@step("I start the Scenario to Remove NFVO if exists in VNF-LCM")
def step_impl(context):
    check_VNFLCM_remove_nfvo()


@step("I start the Scenario to Install Dummy VNF workflow in VNF-LCM")
def step_impl(context):
    install_VNFLCM_dummy_workflow()

    
    
@step("I start the Scenario to Create Vendor_Product For Dummy Node ECDE-VNFLCM")
def step_impl(context):
    create_VNFLCM_dummy_product()
    
    
    
@step("I start the Scenario to Upload Image Resource to Vendor_Product ECDE-VNFLCM")
def step_impl(context):
    upload_VNFLCM_image_resource() 


    
@step("I start the Scenario to Upload Wrapper file Resource to Vendor_Product ECDE-VNFLCM")
def step_impl(context):
    upload_VNFLCM_wrapper_resource()
    
    

@step("I start the Scenario to Get Validation level and Validation stream Id to Validate Product ECDE-VNFLCM")
def step_impl(context):
    get_VNFLCM_val_stream_val_level_id()
    
    

@step("I start the Scenario to Validate Vendor_Product ECDE-VNFLCM")
def step_impl(context):
    validate_VNFLCM_dummy_vendor_product() 
    
    
    
@step("I start the Scenario to Verification of Validation order ECDE-VNFLCM")
def step_impl(context):
    verify_VNFLCM_dummy_validation_order()    
    
   
   
@step("I start the Scenario to Add NFVO if it exits before remove in VNF-LCM")
def step_impl(context):
    #/// this scenario is comment out till the time we get a confirmation from ECDE team for terminate usecase
    # re-adding NFVO creating issue for dummy VNF terminate    

  #Scenario: Add NFVO if it exits before remove in VNF-LCM
    #Given I start the Scenario to Add NFVO if it exits before remove in VNF-LCM 
    #
    #check_VNFLCM_add_nfvo()
    pass     


##########################################################################################################################

@step("I start the Scenario to Create Vendor_Product For Dummy Node ECDE-EVNFM")
def step_impl(context):
    create_EVNFM_dummy_product()


@step("I start the Scenario to Upload Image Resource to Vendor_Product ECDE-EVNFM")
def step_impl(context):
    upload_EVNFM_image_resource()


@step("I start the Scenario to Upload Param Resource to Vendor_Product ECDE-EVNFM")
def step_impl(context):
    upload_EVNFM_paramfile_resource()


@step("I start the Scenario to Get Validation level and Validation stream Id to Validate Product ECDE-EVNFM")
def step_impl(context):
    get_EVNFM_val_stream_val_level_id()


@step("I start the Scenario to Validate Vendor_Product ECDE-EVNFM")
def step_impl(context):
    validate_EVNFM_dummy_vendor_product()


@step("I start the Scenario to Verification of Validation order ECDE-EVNFM")
def step_impl(context):
    verify_EVNFM_dummy_validation_order()

