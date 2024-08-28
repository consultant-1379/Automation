from behave import *
from com_ericsson_do_auto_integration_scripts.ECDE_CDD_NODE_DEPLOYMENT import *

###################################################PRE_REQUISITE #####################################################

@step("I start the Scenario to Generate cdd node pre-req stuff using curl command")
def step_impl(context):
    get_ccd_node_prerequisite()


@step("I start the Scenario to Create a Vendor-Specific Validation Tracks for CDD")
def step_impl(context):
    create_CDD_NODE_validation_track()


@step("I start the Scenario to Assign Vendor-Specific Validation Tracks to CDD TEP")
def step_impl(context):
    assign_CDD_NODE_validation_track()

###################################################DEPLOY JOB #####################################################

@step("I start the Scenario to Create Vendor_Product For CDD Node")
def step_impl(context):
    create_CDD_NODE_product()


@step("I start the Scenario to Get Validation level and Validation stream Id to Validate Product CDD Node")
def step_impl(context):
    get_CDD_val_stream_val_level_id()


@step("I start the Scenario to Validate Vendor_Product CDD Node")
def step_impl(context):
    validate_CDD_NODE_vendor_product()


@step("I start the Scenario to Verification of Validation order CDD Node")
def step_impl(context):
    verify_CDD_NODE_validation_order()

