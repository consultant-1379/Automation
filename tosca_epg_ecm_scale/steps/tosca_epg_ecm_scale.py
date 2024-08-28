# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************

from behave import step
from com_ericsson_do_auto_integration_scripts.EPG_SCALE_HEAL import EpgScaleOperations


@step("I start the Scenario to start scale out")
def step_impl(context):
    EpgScaleOperations.tosca_epg_ecm_scale_out()


@step("I start the Scenario to start scale in")
def step_impl(context):
    EpgScaleOperations.tosca_epg_ecm_scale_in()
