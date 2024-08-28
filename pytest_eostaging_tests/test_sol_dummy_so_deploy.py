
from com_ericsson_do_auto_integration_scripts.DUMMY_SOL_SO_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_create_sol_dummy_nsd():
    """
    This test method is used to Create SOL Dummy NSD
    """
    create_sol_dummy_nsd()



def test_upload_sol_dummy_nsd_package():
    """
    This test method is used to Upload SOL Dummy NSD
    """
    upload_sol_dummy_nsd_package()



def test_onboard_sol_dummy_subsytems():
    """
    This test method is used  to onboard ECM SOL005 adapter subsystem to SO
    """
    onboard_sol_dummy_subsytems()


def test_onboard_sol_dummy_config_template():
    """
    This test method is used  to onboard the configuration templates for SOL Dummy
    """
    onboard_sol_dummy_config_template()


def test_onboard_sol_dummy_service_template():
    """
    This test method is used  to onboard service template
    """
    onboard_sol_dummy_service_template()


def test_create_sol_dummy_network_service():
    """
    This test method is used to create the network service using serviceModel ID
    """
    create_sol_dummy_network_service()


def test_verify_sol_dummy_service_status():
    """
    This test method is used  for polling the state of network service using service ID
    """
    verify_sol_dummy_service_status()
