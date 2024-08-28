
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')

def test_dummy_heal():
    """
    This test method is used to perform heal on dummy vnf type.
    """
    start_heal()


def test_dummy_workflow():
    """
    This test method is used verify DUMMY Node Heal workflow version.
    """
    
    verify_node_heal_workflow_version()

