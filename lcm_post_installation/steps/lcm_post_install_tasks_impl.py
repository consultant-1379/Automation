from behave import *

from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts import VNF_LCM_ECM
from com_ericsson_do_auto_integration_scripts import VNF_LCM_ENM
from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *
log = Logger.get_logger('lcm_post_install_tasks_impl.py')



@step("I have user inputs")
def step_impl(context):

    log.info('Fetching the VNF-LCM server details from cache')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

    context.server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
    context.username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    context.new_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    
    

@step("I proceed to change password for VNF-LCM deployed in static project")
def step_impl(context):
    change_password_first_login('static')
  
  
    
@step("I proceed to change password for VNF-LCM deployed in dynamic project")
def step_impl(context):
    change_password_first_login('dynamic')



@step("I proceed to deploy VNFLCM workflow in static project")
def step_impl(context):
    
    lcm_workflow_deployment('static')
    

@step("I proceed to deploy VNFLCM workflow in dynamic project")
def step_impl(context):
    
    lcm_workflow_deployment('dynamic')



@step("I proceed to integrate ECM with VNF-LCM")
def step_impl(context):
    VNF_LCM_ECM.main(not_enm = False)
    


@step("I proceed to integrate ECM with VNF-LCM without ENM")
def step_impl(context):
    VNF_LCM_ECM.main(not_enm = True)
    
    


@step("I proceed to create gui user and password")
def step_impl(context):
    #create_vnf_gui_user()
    pass
    
        

@step("I proceed to Add the NFVO TLS certificate to the VNF-LCM Services VM")
def step_impl(context):
    install_nfvo_tls_ceritificates()
    
    
@step("I proceed to change password for VNF-LCM Standby Server deployed in dynamic project")
def step_impl(context):    
    change_password_first_login_standby()   
       
    
@step("I proceed to Setup the VNFLCM Services Apache Server for Authentication")
def step_impl(context):
    create_auth_file_vnflcm()
                    

@step("I proceed to change db server password for static project")
def step_impl(context):
    change_db_server_password('static')
    
    
@step("I proceed to change db server password for dynamic project")
def step_impl(context):
    change_db_server_password('dynamic')    
    
    