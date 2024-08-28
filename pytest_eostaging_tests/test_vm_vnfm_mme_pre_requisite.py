from com_ericsson_do_auto_integration_scripts.MME_SO_DEPLOYMENT import *
from start_script import *

def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_add_admin_and_heatstack_roles():
    """
    This test method is used to Add admin and heat_stack_owner roles to project user
    """
    admin_heatstack_rights_mme()
    


def test_transfer_mme_software_to_vnflcm():
    """
    This test method is used to Copy the MME software from HOST blade to VNF-LCM
    """
    transfer_mme_software()
    
    

def test_install_mme_workflow_on_vmvnfm():
    """
    This test method is used to Install the vMME workflow on VM-VNFM
    """
    mme_workflow_deployment_vm_vnfm()
    
def test_generate_sshkeys():
    """
    This test method is used to Generate ssh keys using JBOSS user
    """
    generate_ssh_key_mme()


def test_create_mme_flavours():
    """
    This test method is used to Create Flavors for MME deployment
    """
    create_mme_flavors()
    

def test_create_mme_images():
    """
    This test method is used to Register Images for MME deployment
    """
    create_mme_images()
    
    
def test_upload_ipam_for_mme_depl():
    """
    This test method is used to upload IPAM for MME deployment
    """
    upload_ipam()