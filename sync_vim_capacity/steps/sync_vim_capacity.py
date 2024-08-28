
from behave import *
from com_ericsson_do_auto_integration_scripts.SYNC_VIM_CAPACITY import *




@step("I start the Scenario to create configuration file")
def step_impl(context):    
    create_configuration_file()

@step("I start the Scenario to sync vim capacity")
def step_impl(context):    
    synch_vim_capacity()
    
    
