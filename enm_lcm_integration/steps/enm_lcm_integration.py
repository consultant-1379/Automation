from behave import *

from com_ericsson_do_auto_integration_scripts.ENM_LCM_INTEGRATION import *



@step("I start the Scenario to integrate ENM LCM")
def step_impl(context):
    enm_lcm_integration()
    

    

