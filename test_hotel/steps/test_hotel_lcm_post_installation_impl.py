from behave import *

from com_ericsson_do_auto_integration_scripts.VNF_LCM_ECM import *
from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *

    
@step("I proceed to run ECM steps for Integration")
def step_impl(context):
    execute_ECM_Steps(not_enm = False,test_hotel= True)


@step("I proceed to run LCM steps for Integration")
def step_impl(context):
    execute_VNF_LCM_Steps(not_enm = False,test_hotel= True)
    

@step("I proceed to deploy VNFLCM workflow in static project")
def step_impl(context):
    lcm_workflow_deployment('static')
    

@step("I proceed to change db server password for static project")
def step_impl(context):
    change_db_server_password('static')
    