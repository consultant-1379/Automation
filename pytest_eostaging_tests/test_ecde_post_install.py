from com_ericsson_do_auto_integration_scripts.ECDE_POST_INSTALLATION import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_update_admin_admin_password(context):
    """
    This test method is used to Update admin password first login
    """
    update_admin_password_first_login()

def test_create_ecde_vendor():
    """
    This test method is used to Create a ECDE Vendor
    """
    create_ecde_node_vendor()


def test_create_ecde_node_vendor_user():
    """
    This test method is used to Create a User for ECDE vendor
    """
    create_ecde_node_vendor_user()
    

def test_update_vendor_passwd():
    """
    This test method is used to Update Vendor password first login
    """
    update_vendor_password_first_login()
    
    