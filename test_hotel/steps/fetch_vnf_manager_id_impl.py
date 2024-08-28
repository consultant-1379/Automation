from behave import *

from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *

    
@step("I proceed to fetch VNF manager id")
def step_impl(context):
    fetch_vnf_manager_id()
