from com_ericsson_do_auto_integration_scripts.DC_GATEWAY import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_change_activation_gui_default_passwd():
    """
    This test method is used to change activation gui default password
    """
    change_activation_gui_password()



def test_check_device_if_exist():
    """
    This test method is used to check if device exists
    """
    check_device()



def test_check_device_type():
    """
    This test method is used to check device type
    """
    check_device_type()



def test_check_feature_model():
    """
    Method to check feature model
    """
    check_feature_model()



def test_check_template():
    """
    Method to check template
    """
    check_template()



def test_check_db_entry():
    """
    Method to check db entry
    """
    deletedbentry()



def test_del_network_element_and_route():
    """
    Method to delete network element and route
    """
    delete_ne_and_route()
    

def test_upload_template():
    """
    Method to upload template with device type
    """
    upload_template()


def test_add_network_element_and_route():
    """
    Method to create network element and route
    """
    add_ne_and_route()


def test_create_device():
    """
    Method to create device
    """
    create_device()


def test_add_actvn_managers_entities(context):
   """
   Method to add activation managers entities
   """
   add_activation_managers_entities()
