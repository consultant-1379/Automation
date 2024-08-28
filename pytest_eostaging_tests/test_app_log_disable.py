

from com_ericsson_do_auto_integration_scripts.AppLogEnable import AppLogEnable
from start_script import start_execution


def test_collect_user_input_dit(dit_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB', dit_name, None, None, 'False')


def test_disable_debug_logs():
    """
    This test method is used  to Disable the debug logs for given applications
    """
    AppLogEnable.start_disable_debug_logs(AppLogEnable)
    
