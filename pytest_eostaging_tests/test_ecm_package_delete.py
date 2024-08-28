from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import *
from start_script import *


def test_collect_user_input_DIT(DIT_name,vnf_type):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, vnf_type, 'False')


def test_start_terminating_ECM_packages():
    """
    This method is used to delete all the packages from ECM gui , it also depends upon the input vnf type from jenkins job.
    """
    start_terminating_ECM_packages()


