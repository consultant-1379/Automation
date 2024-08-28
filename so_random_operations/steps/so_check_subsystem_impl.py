
from behave import *
from com_ericsson_do_auto_integration_scripts.SO_RANDOM_OPERATIONS import *
from com_ericsson_do_auto_integration_utilities.Logger import Logger


log = Logger.get_logger('so_check_subsystem_impl.py')


@step('I start the Scenario to Check SO Subsystem accessibility for user')
def step_impl(context):
    check_so_subsytems()
