'''
Created on Sep 27, 2019

@author: emaidns
'''
#This file contains the pre-requisites for ECM and dummy node deployment 

from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ECDE_files_update import *
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_DEPLOYMENT import *



log = Logger.get_logger('ECDE_DUMMY_ECM_DEPLOYMENT.py')



def create_dummy_ecm_vnf_type():
    """
    This method will call the generic method for vnf type creation
    """

    global vnf_type_id

    vnf_type_id = create_dummy_node_vnf_type()
    

def create_dummy_ecm_validation_level():
    """
    This method will call the generic method for validation level creation creation
    """
    global val_level_id

    val_level_id = create_dummy_node_validation_level()
    
def create_ECM_validation_profile():
    try:
        log.info('Start creating the ECM validation profile')
        Report_file.add_line('Start creating the validation profile')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_profile.json'
        name = "AUTO_ECDE_ECM_VALIDATION_PROFILE"
        update_validation_profile_file(file_name,name)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/validation-streams' -d @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '201 Created' in command_output:
            log.info(f'validation profile has been created sucessfully')
            Report_file.add_line(f'validation profile has been created sucessfully ')
        elif 'error.recordWithSameName' in command_output or 'validationStreamNameExists' in command_output:
            log.info(f'validation profile is already exists ')
            Report_file.add_line(f'validation profile is already exists ')
        else:
            log.error('Error creating validation profile with output  %s' , command_output)
            Report_file.add_line('Error creating validation profile with output  ' + command_output)
            assert False

        global val_profile_id

        val_profile_id = get_validation_profile_id(connection, ecde_fqdn, auth_basic,name)

    except Exception as e:
        log.error('Error creating validation profile with exception mesg %s' , str(e))
        Report_file.add_line('Error creating validation profile with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()



def create_ECM_onboarding_system():

    log.info('start creating onboarding system for ECM')

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
    node_name = 'DUMMY-ECM'
    name = 'AUTO_ECM_ONBOARD_SYSTEM'

    file_name = 'create_ecm_onboard_system.json'

    record_exists = get_onboarding_system_id(connection, ecde_fqdn, auth_basic,name,check_exists = True)


    if record_exists == False:

        update_ecm_onboarding_system_file(file_name, name)
        create_onboarding_system(node_name, file_name)

    else:
        log.info('{} already exist for node {} with name {}'.format('Onboarding-system', node_name, name))
        Report_file.add_line('{} already exist for node {} with name {}'.format('Onboarding-system', node_name,
                                                                                name))

        log.info('Going to update the onboarding system')

        ecm_onboarding_id = record_exists
        update_ecm_onboarding_system_file(file_name, name, True, ecm_onboarding_id)
        create_onboarding_system(node_name, file_name, True)

    # connection is getting closed in create onboarding system so opening a new one here
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    global ecm_onboarding_system_id
    ecm_onboarding_system_id = get_onboarding_system_id(connection, ecde_fqdn, auth_basic,name)

    log.info('Finished creating onboarding system for ECM')

    connection.close()

        
 
 
def create_ECM_test_env_profile():
    
    log.info('start creating test env profile system for ECM')

    node_name = 'DUMMY_ECM'

    name = 'AUTO_ECM_TEST_ENV_PROFILE'

    file_name = 'pipeline_tep.json'

    update_pipeline_tep_file(file_name,name,'AUTO_ECM_ONBOARD_SYSTEM','ECM')

    global ecm_test_env_profile_id
    ecm_test_env_profile_id = create_deploy_type_test_env_profile(node_name, file_name,name)

    log.info('Finished creating test env profile for ECM')


def create_ECM_validation_track():
    try:
        log.info('Start creating the ECM validation track')
        Report_file.add_line('Start creating the validation track')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_track.json'

        global vendor_id

        vendor_id = get_vendor_id(connection, ecde_fqdn, auth_basic)

        update_validation_track_file(file_name, vendor_id, vnf_type_id, val_level_id, val_profile_id)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/vendor-specific-validation-tracks' -d @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '201 Created' in command_output:
            log.info(f'validation track has been created sucessfully')
            Report_file.add_line(f'validation track has been created sucessfully ')
        elif 'error.recordWithSameName' in command_output or 'error.duplicateEntry' in command_output:
            log.info(f'validation track is already exists ')
            Report_file.add_line(f'validation track is already exists ')
        else:
            log.error('Error creating validation track with output  ' + command_output)
            Report_file.add_line('Error creating validation track with output  ' + command_output)
            assert False

        # validation track can be identified with val profile(stream) name
        name = 'AUTO_ECDE_ECM_VALIDATION_PROFILE'
        global val_track_id
        val_track_id = get_validation_track_id(connection, ecde_fqdn, auth_basic, name)

    except Exception as e:
        log.error('Error creating validation track with exception mesg ' + str(e))
        Report_file.add_line('Error creating validation track with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()


def assign_ECM_validation_track():
    try:
        log.info('Start assigning the ECM validation track to TEP')
        Report_file.add_line('Start assigning the ECM validation track to TEP')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_track.json'

        global vendor_id

        vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

        update_assign_validation_track_file(file_name,vendor_id, vnf_type_id,val_level_id,val_profile_id,'AUTO_ECDE_ECM_VALIDATION_PROFILE',val_track_id,ecm_test_env_profile_id)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X PUT --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/vendor-specific-validation-tracks-assign?paramtext=AssignTEP' -d @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '200 OK' in command_output:
            log.info(f'validation track has been assigned sucessfully')
            Report_file.add_line(f'validation track has been assigned sucessfully ')
        else:
            log.error('Error assigning validation track with output  %s' , command_output)
            Report_file.add_line('Error assigning validation track with output  ' + command_output)
            assert False


    except Exception as e:
        log.error('Error assigning validation track with exception mesg %s' , str(e))
        Report_file.add_line('Error assigning validation track with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()


def create_ECM_dummy_product():
    
    log.info('Start Creating product for dummy ECDE-ECM deployment')
    
    
    vendor_fqdn, vendor_user, vendor_password = Server_details.ecde_user_details(Server_details, 'vendor')

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
    vendor_auth_basic = Common_utilities.get_auth_basic(Common_utilities, vendor_user, vendor_password)

    global vendor_id
    vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

    node_name = 'ECM_DUMMY'
    product_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'ECDE_ECM_DUMMY')

    file_name = 'create_ecde_product.json'

    global ecm_vnf_type_id
    ecm_vnf_type_id = get_vnf_type_id(connection, ecde_fqdn, auth_basic)

    update_product_file(file_name, product_name, "AUTO_DUMMY", ecm_vnf_type_id, "AUTO_VENDOR", vendor_id)
    create_node_vendor_product(connection, vendor_auth_basic, node_name, file_name)

    global ecm_vendor_product_id

    ecm_vendor_product_id = get_vendor_product_id(connection, ecde_fqdn, vendor_auth_basic, product_name)


    log.info('Finished Creating product for dummy ECDE-ECM deployment')
    
    
def upload_ECM_image_resource():
    
    # Not need of checking resource already exists or not 
    # there might be a case some configuration changes and re-upload the resource on same product 
    # No errors from ECDE if we run the same curl again and again

    resource_file_path = '/var/tmp/deployECDE_DUMMY/DummyECMImage.qcow2'
    resource_name = 'DummyECMImage'
    resource_type = 'IMAGE'
    chunk_number = '0'
    chunk_size = '1'
    global ecm_image_resource_id

    ecm_image_resource_id = upload_node_product_resources(resource_file_path, resource_name, resource_type, ecm_vendor_product_id, chunk_number, chunk_size)
    
def upload_ECM_hotfile_resource():
    
    
    # Not need of checking resource already exists or not 
    # there might be a case some configuration changes and re-upload the resource on same product 
    # No errors from ECDE if we run the same curl again and again 

    resource_file_path = '/var/tmp/deployECDE_DUMMY/Dummy_ECM_RHEL_tmpl.yml'
    resource_name = 'Dummy_ECM_RHEL_tmpl'
    resource_type = 'TMPL'
    chunk_number = '0'
    chunk_size = '1'

    log.info('Fetching the template file from ECM host blade')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

    flavor_name = sit_data._SIT__services_flavor
    external_net_id = sit_data._SIT__external_net_id

    ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')

    dummy_vnf_ip = ecde_data._Ecde__ecde_ecm_dummy_ip

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    ServerConnection.get_file_sftp(connection, resource_file_path,
                                    r'com_ericsson_do_auto_integration_files/ECDE_files/Dummy_ECM_RHEL_tmpl.yml')

    update_dummy_hot_template('Dummy_ECM_RHEL_tmpl.yml', flavor_name, 'DummyECMImage', external_net_id, dummy_vnf_ip)

    ServerConnection.put_file_sftp(connection,
                                    r'com_ericsson_do_auto_integration_files/ECDE_files/Dummy_ECM_RHEL_tmpl.yml',
                                   resource_file_path)

    global ecm_templ_resource_id

    ecm_templ_resource_id = upload_node_product_resources(resource_file_path, resource_name, resource_type, ecm_vendor_product_id ,chunk_number, chunk_size)

def get_ECM_val_stream_val_level_id():

    global ecm_val_level_id

    global ecm_val_stream_id

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
    name = 'AUTO_ECDE_ECM_VALIDATION_PROFILE'
    ecm_val_level_id = get_validation_id(connection, ecde_fqdn, auth_basic)
    ecm_val_stream_id = get_validation_profile_id(connection, ecde_fqdn, auth_basic, name)

    connection.close()

    
def validate_ECM_dummy_vendor_product():
    
    log.info('Start validating the product for dummy node ECM')

    file_name = 'ecde_validate_product.json'

    resources_id_list = [{"id":ecm_image_resource_id}, {"id":ecm_templ_resource_id}]

    update_validate_product_file(file_name, ecm_vendor_product_id, resources_id_list, ecm_val_level_id,
                                 ecm_val_stream_id,ecm_vnf_type_id,vendor_id)

    validate_node_vendor_product('ECM-DUMMY', file_name, ecm_vendor_product_id)

    log.info('Finished validating the product for dummy node ECM')
    
    
def verify_ECM_dummy_validation_order():
    
    get_validation_order_id_status('ECM-DUMMY',3600)
        