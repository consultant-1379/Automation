
from com_ericsson_do_auto_integration_scripts.SO_POST_INSTALLATION import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_create_so_tenant():
    """
    This test method is used to create staging-tenant
    """
    create_so_tenant()



def test_create_user_tenant_admin_role():
    """
    This test method is used to create tenant-admin-user
    """
    create_user_tenant_admin_role()



def test_create_user_so_designer_role():
    """
    This test method is used to create staging-user
    """
    create_user_so_designer_role()


