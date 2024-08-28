from com_ericsson_do_auto_integration_scripts.ETSI_TOSCA_DUMMY_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_remove_old_vnflaf_dir():
    """
    This test method is used to Remove old vnflaf package from vnflcm
    """
    remove_old_vnflaf_dir()

def test_create_flavours_for_etsi_dummy_tosca_depl():
    """
    This test method is used to Create Flavors for ETSI Dummy Tosca deployment
    """
    create_etsi_tosca_dummy_depl_flavours()
    
def test_add_etsi_dummy_tosca_pkg_download_par(context):
    """
    This test method is used to add ETSI Dummy Tosca Package download parameter
    """
    etsi_tosca_package_download_parameter()
    

def test_get_vnfd_id_of_tosca_dummy_node():
    """
    This test method is used to Get zip package name from ECM of Dummy tosca
    """
    get_vnfd_id_tosca_dummy_nodes()
        
def test_update_onboard_file_of_tosca_dummy_node():
    """
    This test method is used to Update Onboard file for ETSI Dummy Tosca Deployment package onboarding
    """
    update_tosca_dummy_node_onboard_file()
    

def test_onboard_dummy_tosca_depl_pkg(context):
    """
    This test method is used to Start on-boarding the Dummy Tosca deployment package
    """
    create_etis_dummy_package_in_cm()



def test_verify_onboarded_etsi_dummy_tosca_pkg():
    """
    This test method is used to Verify on-boarded ETSI Dummy Tosca package
    """
    verify_etis_dummy_package_in_cm()

    

def test_transfer_dummy_image_to_openstack(context):
    """
    This test method is used to transfer ETSI Dummy Tosca image to openstack
    """
    transfer_dummy_image_openstack()


def test_update_dummy_tosca_node_deply_file():
    """
    This test method is used to Update deploy Dummy Tosca ETSI file
    """
    update_tosca_dummy_node_deploy_file()
    
    
def test_deploy_dummy_tosca_pkg():
    """
    This test method is used to Start deploying the ETSI Dummy Tosca Node
    """
    deploy_dummy_tosca_package()
    

def test_verify_etsi_dummy_depl_node():
    """
    This test method is used to Verify ETSI Dummy Tosca deployment Node
    """
    verify_etsi_dummy_deployment()
    

def test_verify_dummy_tosca_workflow_ver():
    """
    This test method is used to Verify ETSI Dummy Tosca Workflow verison
    """
    verfiy_etsi_dummy_tosca_workflow_version()

    


