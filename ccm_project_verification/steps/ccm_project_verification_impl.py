from behave import *

from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import verify_project_exists
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('ccm_project_verification_impl.py')


@step("I start the Scenario to verify project exists in ccm")
def step_impl(context):
    verify_project_exists()
