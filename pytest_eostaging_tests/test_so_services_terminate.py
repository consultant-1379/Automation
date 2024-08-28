from com_ericsson_do_auto_integration_scripts.SO_NODE_DELETION import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')




def test_delete_services_on_so():
    """
    This test method is used to terminate all the services from SO
    """
    start_so_node_deletion()