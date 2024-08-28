from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *


log = Logger.get_logger('IMS_NETWORK_DEPLOYMENT.py')

network_name = ''

def onboard_cscf_network_template():

    global network_name
    network_path = '/var/tmp/CSCF_NETWORK'
    network_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'CSCF_Network')
    upload_file = 'vCSCFnetwork.zip'
    onboard_node_hot_package(network_name, upload_file,network_path)

def deploy_cscf_network_template():

    
    network_path = '/var/tmp/CSCF_NETWORK'
    upload_file = 'sdn_ref_net_vcscf_env.yaml'    
    deploy_network_env_yaml(network_path,upload_file,network_name)


def onboard_mtas_network_template():

    global network_name
    network_path = '/var/tmp/MTAS_NETWORK'
    network_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'MTAS_Network')
    upload_file = 'vMTASnetwork.zip'
    onboard_node_hot_package(network_name, upload_file,network_path)

def deploy_mtas_network_template():

    network_path = '/var/tmp/MTAS_NETWORK'
    upload_file = 'mtas_hot_network_env.yaml'    
    deploy_network_env_yaml(network_path,upload_file,network_name)

def onboard_sbg_network_template():

    global network_name
    
    network_path = '/var/tmp/SBG_NETWORK'
    network_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'SBG_Network')
    upload_file = 'vSBGnetwork.zip'
    onboard_node_hot_package(network_name, upload_file,network_path)

def deploy_sbg_network_template():

    
    network_path = '/var/tmp/SBG_NETWORK'
    upload_file = 'vSBG_Mobile_net_env.yaml' 
    upload_file2 = 'vsbg_sig_nets_dpdk.yaml'   
    deploy_sbg_network_env_yaml(network_path,upload_file,upload_file2,network_name)


def onboard_bgf_network_template():

    global network_name
    
    network_path = '/var/tmp/BGF_NETWORK'
    network_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'BGF_Network')
    upload_file = 'vBGFnetwork.zip'
    onboard_node_hot_package(network_name, upload_file,network_path)


def deploy_bgf_network_template():
    
    network_path = '/var/tmp/BGF_NETWORK'
    upload_file = 'bgf_hot_network_env.yaml'    
    deploy_network_env_yaml(network_path,upload_file,network_name)

