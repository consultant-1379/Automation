from behave import *
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.EPG_MME_DISCOVERY import *



@step("I start the Scenario to Delete EPG and MME record from CMDB")
def step_impl(context):
    delete_epg_and_mme_record_from_cmdb()
   
    
@step("I start the Scenario to create new VDC")
def step_impl(context):
    vdc_creation()
    
  
@step("I start the Scenario to Discover EPG AND MME")
def step_impl(context):
    discovery_of_epg_and_mme()




