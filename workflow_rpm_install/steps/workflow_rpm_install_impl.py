
from behave import *
from com_ericsson_do_auto_integration_scripts.WORKFLOW_INSTALLATION import *

@step("I start the Scenario to Install rpm workflow")
def step_impl(context):
    workflow_rpm_install()
    
    
      
