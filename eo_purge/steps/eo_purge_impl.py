from behave import  *
from com_ericsson_do_auto_integration_scripts.EO_PURGE import *



@step("I start the Scenario to delete and verify helm command and all resources belongs to the deployment")
def step_impl(context):
    eo_purge()
