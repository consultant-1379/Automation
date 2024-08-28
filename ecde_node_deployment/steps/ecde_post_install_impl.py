from behave import *
from com_ericsson_do_auto_integration_scripts.ECDE_POST_INSTALLATION import *


@step("I start the Scenario to Update admin password first login")
def step_impl(context):
    update_admin_password_first_login()




# This is not part of post install now , once we get 3PP testcase we will add the scenario
@step("I start the Scenario to Increase Vendor server heap size for 3PP VNF")
def step_impl(context):
    update_vendor_server_heap()
   


@step("I start the Scenario to Create a ECDE Vendor")
def step_impl(context):
    create_ecde_node_vendor()


@step("I start the Scenario to Create a User for ECDE vendor")
def step_impl(context):
    create_ecde_node_vendor_user()


@step("I start the Scenario to Update Vendor password first login")
def step_impl(context):
    update_vendor_password_first_login()



