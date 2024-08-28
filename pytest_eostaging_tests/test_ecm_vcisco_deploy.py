from com_ericsson_do_auto_integration_scripts.VCISCO_DEPLOY import *
from start_script import *


def test_collect_user_input_DIT(DIT_name):
    """
    This test method is used  to collect all the input parameters from given DIT document name and storing them to use in further tasks of this job
    """
    start_execution('PYTEST-JOB',DIT_name , None, None, 'False')


def test_create_security_groups():
    """
    This test is used to create security group for vcisco deploy
    """
    create_security_groups()


def test_create_vcisco_flavors():
    """
    This test is used to create vcisco flavors on EOCM and transfer to vim . It checks if flavor is already exists or not before creation.
    """
    create_vCisco_flavours()


def test_create_valid9m_flavors():

    """
    This test is used to create valid 9m flavors on EOCM and transfer to vim . It checks if flavor is already exists or not before creation.
    """
    create_valid9m_flavours()


def test_register_vcisco_images():
    """
    This test is used to register the vcisco image that is present on cloud to EOCM .
    """
    register_vCisco_images()



def test_onboard_ovf():
    """
    This test is used to onboard the ovf package as part of vcisco deploy  .
    """
    onboard_ovf()


def test_deploy_ovf():
    """
    This test is used to deploy the ovf package as part of vcisco deploy  .
    """
    deploy_ovf()


def test_deploy_asr_network():
    """
    This test is used to deploy the asr network as part of vcisco deploy  .
    """
    deploy_asr_network()



def test_create_vcisco_bgw_ports():
    """
    This test is used to deploy the bgw ports of vcisco deploy  .
    """
    create_vcisco_bgw_ports()



def test_deploy_vcisco():
    """
    This test is used to deploy the vcisco   .
    """
    deploy_vcisco()


def test_verify_vcisco_deployment():
    """
    This test is used to verify the vcisco  deployment .
    """
    verify_vcisco_deployment()



def test_disable_port():
    """
    This test is used to disable the ports after the deployment.
    """
    disable_port()


def test_register_vcisco_license():
    """
    This test is used to register the vcisco license .
    """
    register_vcisco_license()