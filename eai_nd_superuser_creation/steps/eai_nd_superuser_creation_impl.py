from behave import *
from com_ericsson_do_auto_integration_scripts.EAI_ND_SUPERUSER_CREATION import create_eai_nd_superuser


@step("I start the Scenario to create the EAI ND Super user")
def step_impl(context):
    create_eai_nd_superuser()