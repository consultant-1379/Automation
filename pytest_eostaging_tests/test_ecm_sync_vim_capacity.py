
from com_ericsson_do_auto_integration_scripts.SYNC_VIM_CAPACITY import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_create_configuration_file():
    """
    This test method is used to create configuration file
    """
    create_configuration_file()


def test_synch_vim_capacity():
    """
    This test method is used to sync vim capacity
    """
    synch_vim_capacity()