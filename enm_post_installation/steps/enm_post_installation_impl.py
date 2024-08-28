from behave import *
from com_ericsson_do_auto_integration_scripts.ENM_POST_INSTALLATION import *



@step("I start the Scenario to add roles to admin user")
def step_impl(context):
    add_roles_admin_user()


@step("I start the Scenario to add enm license")
def step_impl(context):
    add_license()


@step("I start the Scenario to check and generate private key")
def step_impl(context):
    add_pem_key_file()
