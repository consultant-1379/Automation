from behave import *
from com_ericsson_do_auto_integration_scripts.EOCM_DUMMY_SCALE import *



@step("I start the Scenario to Scale out of EOCM")
def step_impl(context):
    eocm_scaleout()
    
@step("I start the Scenario to Scale in of EOCM")
def step_impl(context):
    eocm_scalein()
  
@step("I start the Scenario to verify workflow version of eocm dummy scale")
def step_impl(context):
    verify_eocm_dummy_scale_workflow_version()




