
from behave import *
from com_ericsson_do_auto_integration_scripts.SO_RANDOM_OPERATIONS import *
from com_ericsson_do_auto_integration_utilities.Logger import Logger


log = Logger.get_logger('so_log_view_user_impl.py')

@step("I start the Scenario to Create User with SO LogViewer role")
def step_impl(context):
    create_user_so_logviewer_role()

