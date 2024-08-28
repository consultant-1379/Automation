'''
Created on Nov 11, 2019

@author: emaidns
'''
from behave import *
from com_ericsson_do_auto_integration_scripts.ECDE_3PP_ECM_DEPLOYMENT import *


@step("I start the Scenario to Create flavor for 3pp Node ECDE-ECM")
def step_impl(context):
    create_3pp_ecde_flavor()


@step("I start the Scenario to Create Vendor_Product For 3PP Node ECDE-ECM")
def step_impl(context):
    create_ECM_3pp_product()


@step("I start the Scenario to Upload Image Resource to Vendor_Product for 3PP ECDE-ECM")
def step_impl(context):
    upload_ECM_3pp_image_resource()
    
    
    
@step("I start the Scenario to Upload Template Resource to Vendor_Product for 3PP ECDE-ECM")
def step_impl(context):
    upload_ECM_3pp_hotfile_resource() 
    
    

@step("I start the Scenario to Upload bootstrap Config Resource to Vendor_Product for 3PP ECDE-ECM")
def step_impl(context):
    upload_ECM_3pp_bootstrap_resource()
    
    
    
@step("I start the Scenario to Upload authcodes Config Resource to Vendor_Product for 3PP ECDE-ECM")
def step_impl(context):
    upload_ECM_3pp_authcodes_resource()
    
    
    
@step("I start the Scenario to Upload init-cfg Config Resource to Vendor_Product for 3PP ECDE-ECM")
def step_impl(context):
    upload_ECM_3pp_init_resource()
    
    

@step("I start the Scenario to Get Validation level and Validation stream Id to Validate Product for 3PP ECDE-ECM")
def step_impl(context):
    get_ECM_3pp_val_stream_val_level_id() 
        


@step("I start the Scenario to Validate Vendor_Product for 3PP ECDE-ECM")
def step_impl(context):
    validate_ECM_3pp_vendor_product()
        
        

@step("I start the Scenario to Verification of Validation order for 3PP ECDE-ECM")
def step_impl(context):
    verify_ECM_3pp_validation_order()


        
















