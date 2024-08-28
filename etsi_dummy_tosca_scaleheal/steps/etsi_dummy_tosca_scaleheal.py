from behave import *
from com_ericsson_do_auto_integration_scripts.ETSI_DUMMY_TOSCA_SCALEHEAL import *



@step("I start the Scenario to ETSI Dummy Tosca Deployment Scale out")
def step_impl(context):
    etsi_dummy_tosca_depl_scaleout()
    
@step("I start the Scenario to ETSI Dummy Tosca Deployment Scale in")
def step_impl(context):
    etsi_dummy_tosca_depl_scalein()


@step("I start the Scenario to ETSI Dummy Tosca Deployment Scale Heal")
def step_impl(context):
    etsi_dummy_tosca_depl_heal()
        
@step("I start the Scenario to check workflow version of ETSI Dummy Tosca Scale operations")
def step_impl(context):
    verify_etsi_tosca_dummyheal_workflow_verison()
