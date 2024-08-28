'''
Created on Sep 27, 2019

@author: emaidns
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import * 
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_ECM_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *



log = Logger.get_logger('ECDE_DUMMY_VNFLCM_DEPLOYMENT.py')

vnflcm_onboarding_system_id = ''
vnflcm_val_stream_id = ''
vnf_test_env_profile_id = ''
vnflcm_vendor_product_id = ''
wrapper_resource_id = ''
vnflcm_image_resource_id= ''
vnflcm_val_level_id = ''
vnflcm_val_stream_id = ''

def create_VNF_LCM_validation_stream():
    
    log.info('start creating validation stream for ECDE-VNFLCM deployment')
    
    node_name = 'Dummy'
    table_name = 'AVOP_VALIDATION_STREAM'
    column_name = 'VALIDATION_STREAM_NAME'
    record_name = 'AUTO_ECDE_VNFLCM_VALIDATION_STREAM'
    column_string = '''(VALIDATION_STREAM_NAME,DESCRIPTION)'''
    values_tuple = ('AUTO_ECDE_VNFLCM_VALIDATION_STREAM','EO-stagging automation')
    
    create_deploy_type_validation_stream(node_name, table_name, column_name, record_name, column_string, values_tuple)    
    
    id_column_name = 'VALIDATION_STREAM_ID'
    
    global vnflcm_val_stream_id
    vnflcm_val_stream_id = get_record_id(table_name, id_column_name, column_name, record_name)
    
    log.info('Finished creating validation stream for ECDE-VNFLCM deployment')
    
    
def assign_VNFLCM_vnf_type_val_level():
    
    log.info('start assigning validation level and vnf type to validation stream for ECDE-VNFLCM deployment')
     
    node_name = 'Dummy'
    table_name = 'ASSIGNED_ALL_VNF_TYPE_AND_VALIDATION_LEVEL'
    column_name = 'VALIDATION_STREAM_ID'
    record_name = vnflcm_val_stream_id
    column_string = '''(VALIDATION_STREAM_ID,ALL_VNF_TYPE,ALL_VALIDATION_LEVEL)'''
    values_tuple = (vnflcm_val_stream_id,1,1)
    
    assign_vnf_type_val_level_to_val_stream(node_name, table_name, column_name, record_name, column_string, values_tuple)
    
    log.info('Finished assigning validation level and vnf type to validation stream for ECDE-VNFLCM deployment')
    
    
def create_VNFLCM_onboarding_system():

    log.info('start creating onboarding system for VNFLCM')
    

    node_name = 'Dummy'
    table_name = 'AVOP_ONBOARDING_SYSTEM'
    column_name = 'ONBOARDING_SYSTEM_NAME'
    record_name = 'AUTO_VNFLCM_ONBOARD_SYSTEM'
    
    file_name = 'create_vnflcm_onboard_system.json'
    
    record_exists = db_check_record_exists('Onboarding-system', node_name, table_name, column_name, record_name)
    
    if record_exists:
        log.info('{} already exist for node {} with name {}'.format('Onboarding-system',node_name,record_name))
        Report_file.add_line('{} already exist for node {} with name {}'.format('Onboarding-system', node_name, record_name))
        
        log.info('Going to update the onboarding system')
        id_column_name = 'ONBOARDING_SYSTEM_ID'
        
        vnflcm_onboarding_id = get_record_id(table_name, id_column_name, column_name, record_name)
        update_vnflcm_onboarding_system_file(file_name, record_name,True,vnflcm_onboarding_id)
        create_onboarding_system(node_name,file_name, True)
    
    else:
        update_vnflcm_onboarding_system_file(file_name, record_name)
        create_onboarding_system(node_name,file_name)
    
    
    id_column_name = 'ONBOARDING_SYSTEM_ID'
    
    global vnflcm_onboarding_system_id
    vnflcm_onboarding_system_id = get_record_id(table_name, id_column_name, column_name, record_name)
    
    log.info('Finished creating onboarding system for VNFLCM')    
    
    
def create_VNFLCM_test_env_profile():
    
    log.info('start creating test env profile system for VNFLCM')
    
    node_name = 'Dummy'
    table_name = 'AVOP_TEST_ENVIRONMENT_PROFILE'
    column_name = 'TEST_ENVIRONMENT_PROFILE_NAME'
    record_name = 'AUTO_VNFLCM_TEST_ENV_PROFILE'
    column_string = '''(TEST_ENVIRONMENT_PROFILE_NAME,ONBOARDING_SYSTEM_TYPE,ONBOARDING_SYSTEM_ID)'''
    values_tuple = ('AUTO_VNFLCM_TEST_ENV_PROFILE','VNFM',vnflcm_onboarding_system_id)
    
    create_deploy_type_test_env_profile(node_name, table_name, column_name, record_name, column_string, values_tuple)     
    
    id_column_name = 'TEST_ENVIRONMENT_PROFILE_ID'
    
    global vnf_test_env_profile_id
    vnf_test_env_profile_id  = get_record_id(table_name, id_column_name, column_name, record_name)
    
    log.info('Finished creating test env profile for VNFLCM')   
    
    
def create_VNFLCM_validation_track():
    
    log.info('start creating Vendor-Specific Validation Track for VNFLCM')
    
    node_name = 'Dummy'
    table_name = 'AVOP_VENDOR_SPECIFIC_VALIDATION_TRACKS'    
    column_string = '''(VENDOR_ID,VNF_TYPE_ID,VALIDATION_STREAM_ID,VALIDATION_LEVEL_ID,TEP_ID)'''
    column_name = 'VALIDATION_STREAM_ID'
    record_name = vnflcm_val_stream_id
    vnf_vendor_id , vnflcm_vnf_type_id , vnf_val_level_id  =  return_attributes_value()
    
    values_tuple = (vnf_vendor_id,vnflcm_vnf_type_id,vnflcm_val_stream_id,vnf_val_level_id,vnf_test_env_profile_id)
    
    create_deploy_type_validation_track(node_name, table_name, column_name, record_name, column_string, values_tuple)
    
    log.info('Finished creating Vendor-Specific Validation Track for VNFLCM')     

def transfer_vnflaf_dir_to_vnflcm():
    try:
        log.info('start transfering vnflaf package to VNF-LCM ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
        log.info('Removing old vnflaf package from vnflcm')
        command = 'rm -rf /vnflcm-ext/current/vnf_package_repo/vnflaf'
        connection.exec_command(command)

        ServerConnection.put_folder_scp(connection, r'com_ericsson_do_auto_integration_files/vnflaf', '/vnflcm-ext/current/vnf_package_repo/')

        command = 'chmod 777 -R /vnflcm-ext/current/vnf_package_repo/vnflaf'
        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_out = str(stdout.read())
        Report_file.add_line('command_out : ' + command_out)
        log.info('Finished transfering vnflaf package to VNF-LCM ')

    except Exception as e:
        log.info('Error transfering vnflaf package to VNF-LCM ' + str(e))
        Report_file.add_line('Error transfering vnflaf package to VNF-LCM ' + str(e))
        assert False
    finally:
        connection.close()

    
def check_VNFLCM_remove_nfvo():
    
    check_remove_nfvo_in_Vnflcm()
    
def install_VNFLCM_dummy_workflow():
    
    lcm_workflow_deployment('dynamic')       
    
    
def create_VNFLCM_dummy_product():
    
    log.info('Start Creating product for dummy ECDE-VNFLCM deployment')
    
    # Every time product name must be different 
    
    node_name = 'Dummy'
    product_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'ECDE_VNFLCM_DUMMY')
    
    file_name = 'create_ecde_product.json'
    
 
    table_name = 'AVOP_VNF_TYPE'
    column_name = 'VNF_NAME'
    record_name = 'AUTO_DUMMY_3PP'
    vendor_name = 'AUTO_VENDOR'
    id_column_name = 'VNF_TYPE_ID'
    
    log.info('Fetching Id for VNF-TYPE '+record_name)
    
    
    vnflcm_vnf_type_id = get_record_id(table_name, id_column_name, column_name, record_name)
    
    update_product_file(file_name, product_name, record_name, vnflcm_vnf_type_id, vendor_name)
    create_node_vendor_product(node_name,file_name)
    
    
    id_column_name = 'VNF_PRODUCT_ID'
    global vnflcm_vendor_product_id
    column_name = 'PRODUCT_NAME'
    table_name = 'V_PRODUCT_DASHBOARD'
    vnflcm_vendor_product_id = get_record_id(table_name, id_column_name, column_name, product_name)
    
    log.info('Finished Creating product for dummy ECDE-VNFLCM deployment')   
    
    
def upload_VNFLCM_image_resource():
    
    # Not need of checking resource already exists or not 
    # there might be a case some configuration changes and re-upload the resource on same product 
    # No errors from ECDE if we run the same curl again and again 
    
    resource_file_path = '/var/tmp/deployECDE_DUMMY/Dummy_Image.qcow2'
    resource_name = 'Dummy_Image'
    resource_type = 'IMAGE'
    chunk_number = '0'
    chunk_size = '1'
    upload_node_product_resources(resource_file_path,resource_name,resource_type,vnflcm_vendor_product_id,chunk_number,chunk_size)
    
    
    table_name = 'AVOP_PRODUCT_RESOURCE'
    id_column_name = 'RESOURCE_ID'
    column_name = 'RESOURCE_NAME'
    
    column_name2 = 'VNF_PRODUCT_ID'
    record_value = vnflcm_vendor_product_id
    
    
    global vnflcm_image_resource_id
    vnflcm_image_resource_id = get_record_id_two_inputs(table_name, id_column_name, column_name, resource_name, column_name2, record_value)
    
    
def upload_VNFLCM_wrapper_resource():
    
    # Not need of checking resource already exists or not 
    # there might be a case some configuration changes and re-upload the resource on same product 
    # No errors from ECDE if we run the same curl again and again 
    
    
    
    resource_file_path = '/var/tmp/deployECDE_DUMMY/Dummy_VNF_Wrapper.json'
    resource_name = 'Dummy_VNF_Wrapper'
    resource_type = 'PARAMS'
    chunk_number = '0'
    chunk_size = '1'
    
    log.info('Fetching the wrapper file from ECM host blade')
    
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    
    flavor_name = sit_data._SIT__services_flavor
    external_net_id = sit_data._SIT__external_net_id
    
    ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
    
    dummy_vnf_ip = ecde_data._Ecde__ecde_vnflcm_dummy_ip
        
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    
    ServerConnection.get_file_sftp(connection, resource_file_path, r'com_ericsson_do_auto_integration_files/ECDE_files/Dummy_VNF_Wrapper.json')
    
    update_dummy_wrapper_file('Dummy_VNF_Wrapper.json',flavor_name,'Dummy_Image',external_net_id,dummy_vnf_ip)
    
    ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/ECDE_files/Dummy_VNF_Wrapper.json', resource_file_path)
    

    upload_node_product_resources(resource_file_path,resource_name,resource_type,vnflcm_vendor_product_id,chunk_number,chunk_size)
    
    table_name = 'AVOP_PRODUCT_RESOURCE'
    id_column_name = 'RESOURCE_ID'
    column_name = 'RESOURCE_NAME'
    
    column_name2 = 'VNF_PRODUCT_ID'
    record_value = vnflcm_vendor_product_id
    
    
    global wrapper_resource_id
    wrapper_resource_id = get_record_id_two_inputs(table_name, id_column_name, column_name, resource_name, column_name2, record_value)
       


def get_VNFLCM_val_stream_val_level_id():


    global vnflcm_val_level_id
    
    global vnflcm_val_stream_id
    
    vnflcm_val_level_id , vnflcm_val_stream_id = get_node_val_stream_val_level_id('AUTO_INSTANTIATION','AUTO_ECDE_VNFLCM_VALIDATION_STREAM')

    
    
def validate_VNFLCM_dummy_vendor_product():
    
    log.info('Start validating the product for dummy node')
    
    file_name = 'ecde_validate_product.json'
    
    resources_id_list = [vnflcm_image_resource_id , wrapper_resource_id] 
    
    update_validate_product_file(file_name,vnflcm_vendor_product_id,resources_id_list,vnflcm_val_level_id,vnflcm_val_stream_id) 
    
    validate_node_vendor_product('DUMMY',file_name,vendor_product_id)
    
    log.info('Finished validating the product for dummy node')   
    
    
def verify_VNFLCM_dummy_validation_order():  
    
    get_validation_order_id_status('DUMMY',1800)    
    
    
def check_VNFLCM_add_nfvo():
    
    check_add_nfvo_in_Vnflcm()    
          