from behave import step
from com_ericsson_do_auto_integration_scripts.CISM_ZONE_CLUSTER import register_cism_zone, derigester_cism_zone, \
    modify_cism_zone, register_evnfm_cism_zone, deregister_evnfm_cism_zone


##################################EOCM JOB ############################

@step("I start the Scenario to Register CISMS Zone Cluster")
def step_impl(context):
    register_cism_zone()


@step("I start the Scenario to Deregister CISMS Zone Cluster")
def step_impl(context):
    derigester_cism_zone()


@step("I start the Scenario to Modify CISMS Zone Cluster")
def step_impl(context):
    modify_cism_zone()


##################################EVNFM JOB ############################


@step("I start the Scenario to EVNFM Register CISMS Zone Cluster")
def step_impl(context):
    register_evnfm_cism_zone()


@step("I start the Scenario to EVNFM Deregister CISMS Zone Cluster")
def step_impl(context):
    deregister_evnfm_cism_zone()
