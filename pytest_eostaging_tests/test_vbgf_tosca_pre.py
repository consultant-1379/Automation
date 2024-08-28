from com_ericsson_do_auto_integration_scripts.TOSCA_BGF_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.IMS_NETWORK_DEPLOYMENT import *
from start_script import *

def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')




def test_generate_tosca_ssh_keys():
    """
    This test method is used which generate ssh keys using JBOSS user.
    """
    generate_tosca_ssh_key()
    
    

def test_create_tosca_bgf_flavours(context):
    """
    This test method is used to Create TOSCA vBGF flavor and transfer to VIM.
    """
    create_tosca_bgf_flavours()
    


def test_add_pkg_download_parameter():
    """
    This test method is used to Add package download parameter in VNFLCM.
    """
    tosca_bgf_package_download_parameter()



def test_create_tosca_bgf_security_grp():
    """
    This test method is used to Create security group for TOSCA vBGF.
    """
    create_tosca_bgf_security_group()
    
    


def test_onboard_bgf_network_template():
    """
    This test method is used to Onboard Network Stack for BGF node.
    """
    onboard_bgf_network_template()
    



def test_deploy_bgf_network_element(context):
    """
    This test method is used to Deploy Network stack for TOSCA BGF Node.
    """
    deploy_bgf_network_template()
