from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *

from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_change_passwd_first_login():
    """
    This test method is used to change the password at first login
    """
    change_password_first_login('static')
  
def test_lcm_workflow_deployment():
    """
    This test method is used to deploy VNFLCM workflow in static project
    """
    lcm_workflow_deployment('static')
    

def test_integrate_vnf_lcm_with_ecm():
    """
    This test method is used to integrate ECM with VNF-LCM
    """
    VNF_LCM_ECM.main(not_enm = False)
    
    
def test_change_db_server_passwd():
    """
    This test method is used to change db server password for static project
    """
    change_db_server_password('static')
    