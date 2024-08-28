from behave import *
from com_ericsson_do_auto_integration_scripts.CCRC_CNF_DEPLOYMENT import *




@step("I start the Scenario to Upload the app staging target CCD config")
def step_impl(context):
    upload_ccrc_ccd_target_cnfig_app_staging()

