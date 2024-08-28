
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')



def test_domain_creation():
    """
    This test method is used to create the domain
    """
    domain_creation()



def test_site_creation():
    """
    This test method is used to create the site
    """
    site_creation()



def test_vim_registration():
    """
    This test method is used to register the Vim
    """
    vim_registration()



def test_project_creation():
    """
    This test method is used to create the project
    """
    project_creation()




def test_vdc_creation():
    """
    This test method is used to create the virtual data centre
    """
    vdc_creation()




def test_create_block_storage():
    """
    This test method is used to create the block storage
    """
    create_block_storage()



def test_create_key_pair():
    """
    This test method is used to create the key-pair
    """
    create_key_pair()



def test_icmp_rule():
    """
    This test method is used to create the icmp rules
    """
    icmp_rule()


def test_create_internal_network():
    """
    This test method is used to create the internal network
    """
    create_internal_network()


def test_create_external_network():
    """
    This test method is used to create the external network
    """
    create_external_network()


def test_create_bgw_ports():
    """
    This test method is used to create the bgw ports
    """
    create_bgw_ports()
