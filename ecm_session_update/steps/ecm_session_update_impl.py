from behave import *
from com_ericsson_do_auto_integration_scripts.ECM_SESSION_UPDATE import *



@step("I start the Scenario to UPDATE ECM SESSION IN OPEN-AM")
def step_impl(context):
    ecm_session_update()


        

