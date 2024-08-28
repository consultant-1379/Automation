from com_ericsson_do_auto_integration_scripts.COLLECT_RUNTIME_DATA import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_collect_run_time_data():
    """
    Runtime file is the file placed over blade server that keeps the attributes value created in one job and used by another job
    This test method is used to Collect and update in the runtime file if any new attribute exists in local runtime file, just to
    make sure al the attributes exists in the file those are used by automation jobs
    """
    collect_run_time_data()
