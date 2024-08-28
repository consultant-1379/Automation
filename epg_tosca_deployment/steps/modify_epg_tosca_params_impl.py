
from behave import *
from com_ericsson_do_auto_integration_scripts.MODIFY_TOSCA_EPG_PARAMS import *


@step("I start the Scenario to Modify Configurable properties for EPG-TOSCA and verification")
def step_impl(context):
    modify_configurable_prop_tosca_epg()


@step("I start the Scenario to Modify Metadata for EPG-TOSCA and verification")
def step_impl(context):
    modify_metadata_tosca_epg()


@step("I start the Scenario to Modify Extensions for EPG-TOSCA and verification")
def step_impl(context):
    modify_extension_tosca_epg()