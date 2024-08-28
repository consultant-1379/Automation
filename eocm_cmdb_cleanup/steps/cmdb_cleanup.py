"""
implementation file for cmdb_ns_cleanup/cmdb_vapp_cleanup.feature
"""
# pylint: disable=C0116,W0613,E0611,E0102
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

from com_ericsson_do_auto_integration_scripts.CMDB_CLEANUP import (cleanup_network_service_cmdb,
                                                                   cleanup_vapps_cmdb)


@step("I start the Scenario to cleanup network service from cmdb")
def step_impl(context):
    cleanup_network_service_cmdb()


@step("I start the Scenario to cleanup vapps from cmdb")
def step_impl(context):
    cleanup_vapps_cmdb()
