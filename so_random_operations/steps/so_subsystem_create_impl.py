
from behave import *
from com_ericsson_do_auto_integration_scripts.SO_RANDOM_OPERATIONS import *
from com_ericsson_do_auto_integration_utilities.Logger import Logger


log = Logger.get_logger('so_subsystem_create_impl.py')


@step('I start the Scenario to Onboard the ECM and ENM subsystems to SO')
def step_impl(context):
    onboard_so_subsytems()
