# pylint: disable=C0302,C0103,C0301,C0412,E0602,W0621,C0411,R0915,E0602,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612
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
from com_ericsson_do_auto_integration_scripts.DC_GATEWAY import *

@step("I start the Scenario to change activation gui default password")
def step_impl(context):
    change_activation_gui_password()
    

@step("I start the Scenario to Update activation gui password in EOCM")
def step_impl(context):
    update_activation_gui_password_eocm()


@step("I start the Scenario to check_device")
def step_impl(context):
    check_device()


@step("I start the Scenario to check device type")
def step_impl(context):
    check_device_type()


@step("I start the Scenario to check feature model")
def step_impl(context):
    check_feature_model()


@step("I start the Scenario to check template")
def step_impl(context):
    check_template()


@step("I start the Scenario to check db")
def step_impl(context):
    deletedbentry()


@step("I start the Scenario to import_feature_model")
def step_impl(context):
    import_feature_model()


@step("I start the Scenario to upload template with device type")
def step_impl(context):
    upload_template()


@step("I start the Scenario to delete network element and route")
def step_impl(context):
    delete_ne_and_route()


@step("I start the Scenario to create network element and route")
def step_impl(context):
    add_ne_and_route()



@step("I start the Scenario to create_device")
def step_impl(context):
    create_device()



@step("I start the Scenario to add_activation_managers_entities")
def step_impl(context):
   add_activation_managers_entities()
