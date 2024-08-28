
from behave import *

from com_ericsson_do_auto_integration_scripts.SO_DUMMY_SCALE import SO_DUMMY_SCALE as dummy_scale

    
@step("I start the Scenario to do Scale out the Dummy from SO")
def step_impl(context):
    dummy_scale.so_dummy_scale_out(dummy_scale)



@step("I start the Scenario to do Scale In the Dummy from SO")
def step_impl(context):
    dummy_scale.so_dummy_scale_in(dummy_scale)
    
       
