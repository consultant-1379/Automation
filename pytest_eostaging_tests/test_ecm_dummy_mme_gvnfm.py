from com_ericsson_do_auto_integration_scripts.DUMMY_MME_GVNFM_DEPLOYMENT import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')

def test_create_dummy_mme_image():
    """
    This test is used to Register Image Valid9m into the EOCM
    """
    create_dummy_mme_image()


def test_create_dummy_mme_flavors():
    """
        This test is used to Create a Flavor EOST-valid9m_flavor
    """
    create_dummy_mme_flavors()


def test_onboard_dummy_mme_ovf():
    """
        This test is used to Onboard the ECDE_mme_networks_vlan.ovf to cloud manager
    """
    onboard_dummy_mme_ovf()


def test_deploy_dummy_mme_ovf():
    """
        This test is used to Deploy the ECDE_mme_networks_vlan.ovf
    """
    deploy_dummy_mme_ovf()

def test_onboard_dummy_mme_package():
    """
        This test is used to Onboard the ECDE_HOT-MME-DUMY-VNF.zip as a HOT package to cloud manager
    """
    onboard_dummy_mme_package()


def test_deploy_dummy_mme_package():
    """
        This test is used  to Deploy the ECDE_HOT-MME-DUMY-VNF.zip
    """
    deploy_dummy_mme_package()


def test_verify_dummy_mme_deployment():
    """
        This test is used to Verify the Deployment of dummy mme node
    """
    verify_dummy_mme_deployment()