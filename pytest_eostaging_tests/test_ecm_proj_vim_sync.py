from com_ericsson_do_auto_integration_scripts.PROJ_VIM import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_create_sync_openrc_files():
    """
    This test method is used to create sync proj openrc files for static project
    """
    prepare_sync_proj_openrc_files()


def test_create_sync_proj_tenant():
    """
    This test method is sued to create sync proj tenant
    """
    sync_proj_tenant_creation()
     

def test_register_sync_proj_vim():
    """
    This test method is used to Register sync proj VIM
    """
    sync_proj_vim_registration()

def test_create_availability_zone():
    """
    This test method is used to create availability zone
    """
    create_availability_zone()
    
def test_sync_proj_capacity():
    """
    This test method is used to do syc proj capacity
    """
    proj_sync_capacity()
    

def test_create_new_project():
    """
    This test method is used to create new project
    """
    sync_proj_project_creation()


def test_fetch_default_sync_proj_id():
    """
    This test method is used  to fetch sync proj id
    """
    default_sync_proj_id()



def test_add_proj_to_vim():
    """
    This test method is used to add project to vim
    """
    add_project_vim()
    
def test_create_sync_proj_vdc():
    """
    This test method is used to Create sync proj VDC
    """
    sync_proj_vdc_creation()    

