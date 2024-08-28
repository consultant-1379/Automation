from behave import *
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_VNFLCM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import *
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_EVNFM_DEPLOYMENT import *

@step("I start the Scenario to Create VNF-TYPE FOR EVNFM DUMMY NODE")
def step_impl(context):
    # This step is same for all case ECM , VNF-LCM,EVNFM deployment

    create_dummy_evnfm_vnf_type()


@step("I start the Scenario to Create validation levels for EVNFM DUMMY NODE")
def step_impl(context):
    # This step is same for all case ECM , VNF-LCM,EVNFM deployment

    create_dummy_evnfm_validation_level()




@step("I start the Scenario to Create VNF-TYPE FOR ECM DUMMY NODE")
def step_impl(context):
    # This step is same for all case ECM , VNF-LCM,EVNFM deployment

    create_dummy_ecm_vnf_type()


@step("I start the Scenario to Create validation levels for ECM DUMMY NODE")
def step_impl(context):
    # This step is same for all case ECM , VNF-LCM,EVNFM deployment

    create_dummy_ecm_validation_level()


@step("I start the Scenario to Create validation stream for ECM")
def step_impl(context):
    create_ECM_validation_profile()
    
    
    
@step("I start the Scenario to Create validation stream for VNF-LCM")
def step_impl(context):
    create_VNF_LCM_validation_stream()


@step("I start the Scenario to Create validation stream for EVNFM")
def step_impl(context):
    create_EVNFM_validation_profile()


@step("I start the Scenario to Assign VNF-TYPE and Validation level for ECM validation stream")
def step_impl(context):
    assign_ECM_vnf_type_val_level()
    

@step("I start the Scenario to Assign VNF-TYPE and Validation level for VNF-LCM validation stream")
def step_impl(context):
    assign_VNFLCM_vnf_type_val_level()



@step("I start the Scenario to Create Onboarding System for ECM")
def step_impl(context):
    create_ECM_onboarding_system()


@step("I start the Scenario to Create Onboarding System for VNF-LCM")
def step_impl(context):
    create_VNFLCM_onboarding_system() 


@step("I start the Scenario to Create Onboarding System for EVNFM")
def step_impl(context):
    create_EVNFM_onboarding_system()


@step("I start the Scenario to Create Test Environment profile for ECM")
def step_impl(context):
    create_ECM_test_env_profile() 



@step("I start the Scenario to Create Test Environment profile for VNF-LCM")
def step_impl(context):
    create_VNFLCM_test_env_profile()


@step("I start the Scenario to Create Test Environment profile for EVNFM")
def step_impl(context):
    create_EVNFM_test_env_profile()


    

@step("I start the Scenario to Create a Vendor-Specific Validation Tracks for ECM")
def step_impl(context):
    create_ECM_validation_track()    


@step("I start the Scenario to Create a Vendor-Specific Validation Tracks for VNFLCM")
def step_impl(context):
    create_VNFLCM_validation_track()


@step("I start the Scenario to Create a Vendor-Specific Validation Tracks for EVNFM")
def step_impl(context):
    create_EVNFM_validation_track()



@step("I start the Scenario to Assign Vendor-Specific Validation Tracks to EVNFM TEP")
def step_impl(context):
    assign_EVNFM_validation_track()


@step("I start the Scenario to Assign Vendor-Specific Validation Tracks to ECM TEP")
def step_impl(context):
    assign_ECM_validation_track()


@step("I start the Scenario to Transfer vnf package to VNFLCM")
def step_impl(context):
    transfer_vnflaf_dir_to_vnflcm()

