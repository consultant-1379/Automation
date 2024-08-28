# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under  which the
# program(s) have been supplied.
#
# ********************************************************************
from behave import *
from com_ericsson_do_auto_integration_scripts.UDS_POST_INSTALL import UDC_POST_INST as uds_post_inst


@step("I start the Scenario to take backup of uds")
def step_impl(context):
    uds_post_inst.take_backup_of_uds(uds_post_inst)





@step("I start the Scenario to Clean up UDS data")
def step_impl(context):
    uds_post_inst.cleanup_data_on_uds(uds_post_inst)



@step("I start the Scenario to Restart the POD and wait for it to be running")
def step_impl(context):
    uds_post_inst.restart_uds_service_pod(uds_post_inst)

@step("I start the Scenario to delete and restart the Service pod")
def step_impl(context):
    uds_post_inst.delete_and_restart_pods(uds_post_inst)
