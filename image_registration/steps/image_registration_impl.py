from behave import *

from com_ericsson_do_auto_integration_scripts.ECM_RANDOM_OPERATIONS import *


@step("I start the Scenario to register the image")
def step_impl(context):
    start_image_registration()
    

