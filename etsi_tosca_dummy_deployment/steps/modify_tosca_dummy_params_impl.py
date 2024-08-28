
from behave import *
from com_ericsson_do_auto_integration_scripts.MODIFY_TOSCA_DUMMY_PARAMS import *


@step("I start the Scenario to Modify Configurable properties for TOSCA-DUMMY and verification")
def step_impl(context):
    modify_configurable_prop_tosca_dummy()


@step("I start the Scenario to Modify Metadata for TOSCA-DUMMY and verification")
def step_impl(context):
    modify_metadata_tosca_dummy()


@step("I start the Scenario to Modify Extensions for TOSCA-DUMMY and verification")
def step_impl(context):
    modify_extension_tosca_dummy()

