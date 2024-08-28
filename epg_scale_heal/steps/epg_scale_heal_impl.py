from behave import step
from com_ericsson_do_auto_integration_scripts.EPG_SCALE_HEAL import EpgScaleOperations as epg_scale_ope


@step("I start the Scenario to start scale out")
def step_impl(context):
    epg_scale_ope.epg_ecm_scale_out()


@step("I start the Scenario to start heal")
def step_impl(context):
    epg_scale_ope.epg_heal(epg_scale_ope)


@step("I start the Scenario to start scale in")
def step_impl(context):
    epg_scale_ope.epg_ecm_scale_in()


@step("I start the Scenario to start tosca EPG heal")
def step_impl(context):
    epg_scale_ope.tosca_epg_heal(epg_scale_ope)
