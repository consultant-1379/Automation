from behave import step
from com_ericsson_do_auto_integration_scripts.APP_LOG_VERIFICATION import (evnfm_log_verify, so_logviewer_log_verify,
                                                                           so_subsystem_log_verify,wano_log_verify)


@step("I start the Scenario to check the log hits for evnfm")
def step_impl(context):
    evnfm_log_verify()


@step("I start the Scenario to check the log hits for SO logviewer")
def step_impl(context):
    so_logviewer_log_verify()
    

@step("I start the Scenario to check the log hits for SO subsystem")
def step_impl(context):
    so_subsystem_log_verify()
   

@step("I start the Scenario to check the log hits for wano")
def step_impl(context):
    wano_log_verify()
