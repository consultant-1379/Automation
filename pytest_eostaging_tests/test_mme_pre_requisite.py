from com_ericsson_do_auto_integration_scripts.MME_SO_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_remove_LCM_entry_mme():
    """
    This test method is used to clean old lcm entry from terminal
    """
    remove_LCM_entry_mme()




def test_admin_heatstack_rights_mme():
    """
    This test method is used to Add admin and heat_stack_owner roles to project user
    """
    admin_heatstack_rights_mme()



def test_update_lcm_password_mme():
    """
    This test method is used to  Update VNFLCM OSS Password
    """
    update_lcm_password_mme()


def test_transfer_mme_software():
    """
    This test method is used  to Copy the MME software from HOST blade to VNF-LCM
    """
    transfer_mme_software()


def test_mme_workflow_deployment():
    """
    This test method is used  to Install the MME workflow on VNF-LCM
    """
    mme_workflow_deployment()

def test_update_db_table():
    """
    This test method is used to Update db table with MME entries for instantiate and terminate

    """
    update_db_table()


def test_generate_ssh_key_mme():
    """
    This test method is used  to Generate ssh keys using JBOSS user
    """
    generate_ssh_key_mme()


def test_create_mme_flavors():
    """
    This test method is used  to Create Flavors for MME deployment , coming from DIT.
    """
    create_mme_flavors()


def test_create_mme_images():
    """
    This test method is used  to Register Images for MME deployment , coming from DIT.
    """
    create_mme_images()


def test_upload_ipam():
    """
    This test method is used to upload IPAM for MME deployment
    """
    upload_ipam()

