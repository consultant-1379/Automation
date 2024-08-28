from behave import *

from com_ericsson_do_auto_integration_scripts.SO_TOSCA_EPG_SCALE import *


@step("I start the Scenario to start scale out")
def step_impl(context):
    so_tosca_epg_scale_out()


@step("I start the Scenario to start scale in")
def step_impl(context):
    so_tosca_epg_scale_in()
