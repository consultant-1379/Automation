from com_ericsson_do_auto_integration_scripts.EPG_SO_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from start_script import *

def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')

def test_add_admin_heatstack_roles():
    """
    This test method is used to Add admin and heat_stack_owner roles to project user
    """
    admin_heatstack_rights()


def test_transfer_epg_software():
    """
    This test method is used to Copy the EPG software from HOST blade to VNF-LCM
    """
    transfer_epg_software()
    
def test_workflow_Depl_on_vmvnfm(context):
    """
    This test method is used to Install the vEPG workflow on VM-VNFM
    """
    workflow_deployment()
    
def test_generate_ssh_keys():
    """
    This test method is used to Generate ssh keys using JBOSS user
    """
    generate_ssh_key()
    
def test_create_epg_flavours():
    """
    This test method is used to Create Flavors for EPG deployment
    """
    create_epg_flavours()
    
def test_register_epg_images():
    """
    This test method is used to Register Images for EPG deployment
    """
    register_epg_images()
    