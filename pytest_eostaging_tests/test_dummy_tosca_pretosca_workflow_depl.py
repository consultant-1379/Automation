from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_install_tosca_pretosca_workflow():
    """
    This test method is used install work-flow
    """
    install_tosca_pretosca_workflow()


def test_modify_workflow_bundle_descriptor():
    """
    This test method is used to modify work-flow bundle descriptor
    """
    modify_workflow_bundle_descriptor()
