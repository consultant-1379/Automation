from behave import *

from com_ericsson_do_auto_integration_scripts.SO_POST_INSTALLATION import *


@step("I start the Scenario to create staging-tenant")
def step_impl(context):
    create_so_tenant()
    


@step("I start the Scenario to create tenant-admin-user")
def step_impl(context):
    create_user_tenant_admin_role()
    


@step("I start the Scenario to create staging-user")
def step_impl(context):
    create_user_so_designer_role()
    
