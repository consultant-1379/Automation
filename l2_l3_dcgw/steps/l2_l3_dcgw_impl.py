from behave import *

from com_ericsson_do_auto_integration_scripts.L2_L3_DCGW import *


@step("I start the Scenario create DC-GW in EO-CM")
def step_impl(context):
    create_dcgw_eo_cm()


@step("I start the Scenario verify Creation of DC-GW in EO-CM")
def step_impl(context):
    verify_l2_l3_dcgw_creation()


@step("I start the Scenario create VRF on DCGW in EO-CM")
def step_impl(context):
    create_vrf_dcgw()

