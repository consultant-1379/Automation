from com_ericsson_do_auto_integration_scripts.MODIFY_TOSCA_DUMMY_PARAMS import *

from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_modify_conf_prop_for_tosca_dummy():
    """
    This test method is used to Modify Configurable properties for TOSCA-DUMMY and verification
    """
    modify_configurable_prop_tosca_dummy()


def test_modify_metadata():
    """
    This test method is used to Modify Metadata for TOSCA-DUMMY and verification
    """
    modify_metadata_tosca_dummy()

def test_modify_extensions_for_toscadummy():
    """
    This test method is used to Modify Extensions for TOSCA-DUMMY and verification
    """
    modify_extension_tosca_dummy()



