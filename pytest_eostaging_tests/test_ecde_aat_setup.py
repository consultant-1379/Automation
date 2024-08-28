from com_ericsson_do_auto_integration_scripts.ECDE_TEST_ENV_SETUP import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_create_aat_tool():
    """
    This test method is used to create AAT tool in ECDE Test tools"
    """
    create_ecde_aat_tool()


def test_create_testcase_to_aat_tool():
    """
    This test method is used to Create a testcase under Test tool
    """
    add_testcase_to_aat_tool()
   

def test_add_ecde_testsuite():
    """
    This test method is used to Create a test-suite with test-case added to Test tool
    """
    add_ecde_testsuit()
