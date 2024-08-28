'''
Created on Nov 18, 2019

@author: emaidns
'''


from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger

from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import *
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_scripts.ECM_POST_INSTALLATION import *
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import *
from com_ericsson_do_auto_integration_utilities.ECDE_files_update import *
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_DEPLOYMENT import *

log = Logger.get_logger('ECDE_3PP_ECM_DEPLOYMENT.py')


vnf_type_id_3pp = ''
vendor_product_id_3pp = ''
resources_id_list_3pp = []
val_level_id_3pp = ''
val_stream_id_3pp = ''



def create_3pp_ecde_flavor():
    
    log.info('start creating ecde flavor')
    Report_file.add_line('start creating ecde flavor')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    openrc_filename = EPIS_data._EPIS__openrc_filename
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    tenant_name = sit_data._SIT__tenantName
    flavor_name = '3pp_ecde_flavor'

    flavor_exists = check_flavor_exists(openrc_filename, openstack_ip, username, password, flavor_name)
    if flavor_exists:
        log.info('Flavor with name ' + flavor_name + ' already exists in cloud')
        Report_file.add_line('Flavor with name ' + flavor_name + ' already exists in cloud')
    else:
        log.info('Flavor with name ' + flavor_name + ' does not  exists in cloud')
        Report_file.add_line('Flavor with name ' + flavor_name + ' does not  exists in cloud')
        name = flavor_name
        
        update_any_flavor_file(name, 2, 6114, 80, tenant_name)
        update_transfer_flavour_file()
  
        create_flavour('flavour.json', 'flavour_transfer.json', name)

    log.info('Finished creating ecde flavors')
    Report_file.add_line('Finished creating ecde flavors')
    
    
    
def create_ECM_3pp_product():
    
    log.info('Start Creating product for 3PP ECDE-ECM deployment')
    
    
    # Every time product name would be different but not mandatory in this usecase 
    
    node_name = '3PP'

    product_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'ECDE_ECM_3PP')
    
    file_name = 'create_ecde_product.json'
    
    table_name = 'AVOP_VNF_TYPE'
    column_name = 'VNF_NAME'
    record_name = 'AUTO_DUMMY_3PP'
    vendor_name = 'AUTO_VENDOR'
    id_column_name = 'VNF_TYPE_ID'
    
    log.info('Fetching Id for VNF-TYPE '+record_name)
    
    global vnf_type_id_3pp
    vnf_type_id_3pp = get_record_id(table_name, id_column_name, column_name, record_name)
    
    update_product_file(file_name, product_name, record_name, vnf_type_id_3pp, vendor_name)
    create_node_vendor_product(node_name,file_name)
    
    
    id_column_name = 'VNF_PRODUCT_ID'
    global vendor_product_id_3pp
    column_name = 'PRODUCT_NAME'
    table_name = 'V_PRODUCT_DASHBOARD'
    vendor_product_id_3pp = get_record_id(table_name, id_column_name, column_name, product_name)
    
    log.info('Finished Creating product for dummy ECDE-ECM deployment')
    
    
    
def upload_ECM_3pp_image_resource():
    
    # Not need of checking resource already exists or not 
    # there might be a case some configuration changes and re-upload the resource on same product 
    # No errors from ECDE if we run the same curl again and again 
    
    resource_file_path = '/var/tmp/deployECDE_3PP/Image_3PP_automation.qcow2'
    resource_name = 'Image_3PP_automation'
    resource_type = 'IMAGE'
    chunk_number = '0'
    chunk_size = '1'
    upload_node_product_resources(resource_file_path,resource_name,resource_type,vendor_product_id_3pp,chunk_number,chunk_size)
    
    
    table_name = 'AVOP_PRODUCT_RESOURCE'
    id_column_name = 'RESOURCE_ID'
    column_name = 'RESOURCE_NAME'
    
    column_name2 = 'VNF_PRODUCT_ID'
    record_value = vendor_product_id_3pp
    
    global resources_id_list_3pp
    
    image_resource_id_3pp = get_record_id_two_inputs(table_name, id_column_name, column_name, resource_name, column_name2, record_value)  
    resources_id_list_3pp.append(image_resource_id_3pp)  
        
def upload_ECM_3pp_hotfile_resource():

    # Not need of checking resource already exists or not 
    # there might be a case some configuration changes and re-upload the resource on same product 
    # No errors from ECDE if we run the same curl again and again 
    
     
    
    resource_file_path = '/var/tmp/deployECDE_3PP/Template_3PP_automation.yaml'
    resource_name = 'Template_3PP_automation'
    resource_type = 'TMPL'
    chunk_number = '0'
    chunk_size = '1'
    
    log.info('Fetching the template file from ECM host blade')
    
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    
    flavor_name = 'CM-3pp_ecde_flavor'
    external_net_id = sit_data._SIT__external_net_id
    
    ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
    
    vnf_3pp_ips = ecde_data._Ecde__ecde_ecm_3pp_ips
    
    
    cloud_type = sit_data._SIT__cloudManagerType
    ecm_environment = ecm_host_data._Ecm_core__enviornment
    network_name = 'P3_'+ cloud_type +'01_' + ecm_environment + '_PROV'
        
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    
    ServerConnection.get_file_sftp(connection, resource_file_path, r'com_ericsson_do_auto_integration_files/ECDE_files/Template_3PP_automation.yaml')
    
    update_3pp_hot_template('Template_3PP_automation.yaml',flavor_name,'Image_3PP_automation',external_net_id,vnf_3pp_ips,network_name)
    
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/ECDE_files/Template_3PP_automation.yaml', resource_file_path)
    

    upload_node_product_resources(resource_file_path,resource_name,resource_type,vendor_product_id_3pp,chunk_number,chunk_size)
    
    table_name = 'AVOP_PRODUCT_RESOURCE'
    id_column_name = 'RESOURCE_ID'
    column_name = 'RESOURCE_NAME'
    
    column_name2 = 'VNF_PRODUCT_ID'
    record_value = vendor_product_id_3pp
    
    
    global resources_id_list_3pp
    tmpl_resource_id_3pp = get_record_id_two_inputs(table_name, id_column_name, column_name, resource_name, column_name2, record_value)
    resources_id_list_3pp.append(tmpl_resource_id_3pp)
    
def upload_ECM_3pp_bootstrap_resource():
    
    resource_file_path = '/var/tmp/deployECDE_3PP/bootstrap.xml'
    resource_name = 'bootstrap'
    resource_type = 'CONFIG'
    chunk_number = '0'
    chunk_size = '1'
    upload_node_product_resources(resource_file_path,resource_name,resource_type,vendor_product_id_3pp,chunk_number,chunk_size)
    
    
    table_name = 'AVOP_PRODUCT_RESOURCE'
    id_column_name = 'RESOURCE_ID'
    column_name = 'RESOURCE_NAME'
    
    column_name2 = 'VNF_PRODUCT_ID'
    record_value = vendor_product_id_3pp
    
    global resources_id_list_3pp
    
    bootstrap_resource_id_3pp = get_record_id_two_inputs(table_name, id_column_name, column_name, resource_name, column_name2, record_value)  
    resources_id_list_3pp.append(bootstrap_resource_id_3pp)  
    

def upload_ECM_3pp_authcodes_resource():
    
    resource_file_path = '/var/tmp/deployECDE_3PP/authcodes'
    resource_name = 'authcodes'
    resource_type = 'CONFIG'
    chunk_number = '0'
    chunk_size = '1'
    upload_node_product_resources(resource_file_path,resource_name,resource_type,vendor_product_id_3pp,chunk_number,chunk_size)
    
    
    table_name = 'AVOP_PRODUCT_RESOURCE'
    id_column_name = 'RESOURCE_ID'
    column_name = 'RESOURCE_NAME'
    
    column_name2 = 'VNF_PRODUCT_ID'
    record_value = vendor_product_id_3pp
    
    global resources_id_list_3pp
    
    authcodes_resource_id_3pp = get_record_id_two_inputs(table_name, id_column_name, column_name, resource_name, column_name2, record_value)  
    resources_id_list_3pp.append(authcodes_resource_id_3pp)  
    
    
def upload_ECM_3pp_init_resource():
    
    resource_file_path = '/var/tmp/deployECDE_3PP/init-cfg.txt'
    resource_name = 'init-cfg'
    resource_type = 'CONFIG'
    chunk_number = '0'
    chunk_size = '1'
    upload_node_product_resources(resource_file_path,resource_name,resource_type,vendor_product_id_3pp,chunk_number,chunk_size)
    
    
    table_name = 'AVOP_PRODUCT_RESOURCE'
    id_column_name = 'RESOURCE_ID'
    column_name = 'RESOURCE_NAME'
    
    column_name2 = 'VNF_PRODUCT_ID'
    record_value = vendor_product_id_3pp
    
    global resources_id_list_3pp
    
    init_resource_id_3pp = get_record_id_two_inputs(table_name, id_column_name, column_name, resource_name, column_name2, record_value)  
    resources_id_list_3pp.append(init_resource_id_3pp)      
        
def get_ECM_3pp_val_stream_val_level_id():  
          
    global val_level_id_3pp
    global val_stream_id_3pp
    
    val_level_id_3pp , val_stream_id_3pp = get_node_val_stream_val_level_id('AUTO_INSTANTIATION','AUTO_ECDE_ECM_VALIDATION_STREAM')
    
    
def validate_ECM_3pp_vendor_product():
    
    log.info('Start validating the product for 3PP node')
    
    file_name = 'ecde_validate_product.json'
    
    
    update_validate_product_file(file_name,vendor_product_id_3pp,resources_id_list_3pp,val_level_id_3pp,val_stream_id_3pp) 
    
    validate_node_vendor_product('3PP',file_name,vendor_product_id_3pp)
    
    log.info('Finished validating the product for 3PP node')
    
    
def verify_ECM_3pp_validation_order():
    
    get_validation_order_id_status('3PP',7200)        
               