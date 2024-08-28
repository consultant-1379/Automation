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
from behave import *

from com_ericsson_do_auto_integration_scripts.VM_VNFM_LCM_ECM_INTEGRATION import *


@step("I proceed to Register Test Hotle  VM VNFM")
def step_impl(context):
    register_vm_vnfm('TEST-HOTEL')


@step("I proceed to Add Test Hotel NFVO in VM VNFM")
def step_impl(context):
    add_nfvo_vm_vnfm('TEST-HOTEL')
