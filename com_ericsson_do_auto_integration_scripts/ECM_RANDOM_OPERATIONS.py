
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.MME_SO_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.EPG_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities

log = Logger.get_logger('ECM_RANDOM_OPERATIONS.py')


def start_image_registration():
    
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    vnf_type = sit_data._SIT__vnf_type
    log.info('Starting script : Registering Image for: '+vnf_type)
    Report_file.add_line('Starting script : Registering Image for: ' + vnf_type)
    

    if vnf_type == 'DUMMY':
        
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        image_name = EPIS_data._EPIS__image_name
        
        image_exists = check_image_registered(connection, image_name, token, core_vm_hostname)
        
        if image_exists:
            Report_file.add_line('Image with name ' + image_name + ' already registered in cloud manager')
        else:
            update_registerImage_file('RegisterImage.json')
            image_registration('RegisterImage.json')
    
    elif vnf_type == 'EPG': 
    
        register_epg_images()
    
    elif vnf_type == 'MME':
        
        create_mme_images()
        
    else:
        
        log.error('VNF type not supported, check the vnf type')
        assert False

def start_flavour_creation():
    
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    vnf_type = sit_data._SIT__vnf_type
    log.info('Starting script : Creating flavour for: '+vnf_type)
    Report_file.add_line('Starting script : Creating flavour for: ' + vnf_type)
    

    if vnf_type == 'DUMMY':
        
        openstack_ip,username,password,openrc_filename= Server_details.openstack_host_server_details(Server_details)
        
        flavour_name = EPIS_data._EPIS__flavour_name
        flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavour_name)
        
        if flavor_exists:
            log.info('Flavor with name ' + flavour_name + ' already exists in CEE and ECM')
            Report_file.add_line('Flavor with name ' + flavour_name + ' already exists in CEE and ECM')
        
        else:
            name = flavour_name[3:]
            update_flavour_file()
            update_transfer_flavour_file()
            create_flavour('flavour.json', 'flavour_transfer.json', name)
    
    elif vnf_type == 'EPG': 
    
        create_epg_flavours()
    
    elif vnf_type == 'MME':
        
        create_mme_flavors()
        
    else:
        
        log.error('VNF type not supported, check the vnf type')
        assert False

    
    