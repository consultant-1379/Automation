
from behave import *
from com_ericsson_do_auto_integration_scripts.WANO_USECASES import *

@step("I start the Scenario to Create a service in Wano application")
def step_impl(context):
    create_wano_service()
    
    
      
