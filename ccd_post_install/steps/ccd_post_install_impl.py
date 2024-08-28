from behave import step
from com_ericsson_do_auto_integration_scripts.CCD_POST_INSTALL import (
    distribute_egad_certs, distribute_egad_certs_cn, update_authorize_keys)

@step("I start the Scenario to Distribute EGAD Certificates")
def step_impl(context):
    distribute_egad_certs()
        
@step("I start the Scenario to Update Authorize Keys")
def step_impl(context):
    update_authorize_keys()    
    
@step("I start the Scenario to Distribute EGAD Certificates CLOUD NATIVE")
def step_impl(context):
    distribute_egad_certs_cn()
