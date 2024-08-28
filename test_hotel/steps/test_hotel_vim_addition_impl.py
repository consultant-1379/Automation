from behave import *

from com_ericsson_do_auto_integration_scripts.VNF_LCM_ECM import *

    
@step("I proceed to add vim for test hotel")
def step_impl(context):
    test_hotel_vim_addition(not_enm = False)

    