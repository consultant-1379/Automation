'''
Created on Apr 21, 2020
Corona times
@author: emaidns
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_ECM_DEPLOYMENT import *

log = Logger.get_logger('ECDE_DUMMY_EVNFM_DEPLOYMENT.py')


def create_dummy_evnfm_vnf_type():
    """
    This method will call the generic method for vnf type creation
    """

    global vnf_type_id

    vnf_type_id = create_dummy_node_vnf_type()

def create_dummy_evnfm_validation_level():

    """
    This method will call the generic method for validation level creation creation
    """

    global val_level_id

    val_level_id = create_dummy_node_validation_level()


def create_EVNFM_validation_profile():
    try:
        log.info('Start creating the EVNFM validation profile')
        Report_file.add_line('Start creating the validation profile')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_profile.json'
        name = "AUTO_ECDE_EVNFM_VALIDATION_PROFILE"
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
            log.error('Error creating validation profile with output  ' + command_output)
            Report_file.add_line('Error creating validation profile with output  ' + command_output)
            assert False

        global val_profile_id

        val_profile_id = get_validation_profile_id(connection, ecde_fqdn, auth_basic,name)

    except Exception as e:
        log.error('Error creating validation profile with exception mesg ' + str(e))
        Report_file.add_line('Error creating validation profile with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()


def create_EVNFM_onboarding_system():
    log.info('start creating onboarding system for EVNFM')

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
    node_name = 'DUMMY-EVNFM'
    name = 'AUTO_EVNFM_ONBOARD_SYSTEM'

    file_name = 'create_evnfm_onboard_system.json'

    record_exists = get_onboarding_system_id(connection, ecde_fqdn, auth_basic,name,check_exists = True)


    if record_exists == False:
        update_evnfm_onboarding_system_file(file_name, name)
        create_onboarding_system(node_name, file_name)

    else:
        log.info('{} already exist for node {} with name {}'.format('Onboarding-system', node_name, name))
        Report_file.add_line('{} already exist for node {} with name {}'.format('Onboarding-system', node_name,
                                                                                name))

        log.info('Going to update the onboarding system')

        evnfm_onboarding_id = record_exists
        update_evnfm_onboarding_system_file(file_name, name, True, evnfm_onboarding_id)
        create_onboarding_system(node_name, file_name, True)

    # connection is getting closed in create onboarding system so opening a new one here
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    global evnfm_onboarding_system_id
    evnfm_onboarding_system_id = get_onboarding_system_id(connection, ecde_fqdn, auth_basic,name)

    log.info('Finished creating onboarding system for EVNFM')

    connection.close()


def create_EVNFM_test_env_profile():
    log.info('start creating test env profile system for EVNFM')

    node_name = 'DUMMY_EVNFM'

    name = 'AUTO_EVNFM_TEST_ENV_PROFILE'

    file_name = 'pipeline_tep.json'

    update_pipeline_tep_file(file_name,name,'AUTO_EVNFM_ONBOARD_SYSTEM','EVNFM')

    global evnfm_test_env_profile_id
    evnfm_test_env_profile_id = create_deploy_type_test_env_profile(node_name, file_name,name)

    log.info('Finished creating test env profile for EVNFM')


def create_EVNFM_validation_track():
    try:
        log.info('Start creating the EVNFM validation track')
        Report_file.add_line('Start creating the validation track')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_track.json'

        global vendor_id

        vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

        update_validation_track_file(file_name,vendor_id, vnf_type_id,val_level_id,val_profile_id)

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
        name = 'AUTO_ECDE_EVNFM_VALIDATION_PROFILE'
        global val_track_id
        val_track_id = get_validation_track_id(connection, ecde_fqdn, auth_basic, name)

    except Exception as e:
        log.error('Error creating validation track with exception mesg ' + str(e))
        Report_file.add_line('Error creating validation track with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()


def assign_EVNFM_validation_track():
    try:
        log.info('Start assigning the EVNFM validation track to TEP')
        Report_file.add_line('Start assigning the EVNFM validation track to TEP')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_track.json'

        global vendor_id

        vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

        update_assign_validation_track_file(file_name,vendor_id, vnf_type_id,val_level_id,val_profile_id,'AUTO_ECDE_EVNFM_VALIDATION_PROFILE',val_track_id,evnfm_test_env_profile_id)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X PUT --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/vendor-specific-validation-tracks-assign?paramtext=AssignTEP' -d @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '200 OK' in command_output:
            log.info(f'validation track has been assigned sucessfully')
            Report_file.add_line(f'validation track has been assigned sucessfully ')
        else:
            log.error('Error assigning validation track with output  ' + command_output)
            Report_file.add_line('Error assigning validation track with output  ' + command_output)
            assert False


    except Exception as e:
        log.error('Error assigning validation track with exception mesg ' + str(e))
        Report_file.add_line('Error assigning validation track with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()




def create_EVNFM_dummy_product():
    log.info('Start Creating product for dummy ECDE-EVNFM deployment')

    # Every time product name must be different

    vendor_fqdn, vendor_user, vendor_password = Server_details.ecde_user_details(Server_details, 'vendor')

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
    vendor_auth_basic = Common_utilities.get_auth_basic(Common_utilities, vendor_user, vendor_password)

    global evnfm_vendor_id
    evnfm_vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

    node_name = 'EVNFM_DUMMY'
    product_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'ECDE_EVNFM_DUMMY')

    file_name = 'create_ecde_product.json'

    global evnfm_vnf_type_id
    evnfm_vnf_type_id = get_vnf_type_id(connection,ecde_fqdn,auth_basic)

    update_product_file(file_name, product_name, "AUTO_DUMMY", evnfm_vnf_type_id, "AUTO_VENDOR",evnfm_vendor_id)
    create_node_vendor_product(connection, vendor_auth_basic ,node_name, file_name)

    global evnfm_vendor_product_id

    evnfm_vendor_product_id = get_vendor_product_id(connection, ecde_fqdn, vendor_auth_basic, product_name)

    log.info('Finished Creating product for dummy ECDE-EVNFM deployment')


def upload_EVNFM_image_resource():
    # Not need of checking resource already exists or not
    # there might be a case some configuration changes and re-upload the resource on same product
    # No errors from ECDE if we run the same curl again and again

    resource_file_path = '/var/tmp/deployECDE_DUMMY/Dummy_Evnfm_Image.csar'
    resource_name = 'Dummy_Evnfm_Image'
    resource_type = 'IMAGE'
    chunk_number = '0'
    chunk_size = '1'
    global evnfm_image_resource_id

    evnfm_image_resource_id = upload_node_product_resources(resource_file_path, resource_name, resource_type, evnfm_vendor_product_id,
                                  chunk_number, chunk_size)

def upload_EVNFM_paramfile_resource():
    # Not need of checking resource already exists or not
    # there might be a case some configuration changes and re-upload the resource on same product
    # No errors from ECDE if we run the same curl again and again

    resource_file_path = '/var/tmp/deployECDE_DUMMY/Dummy_Evnfm_Param.json'
    resource_name = 'Dummy_Evnfm_Param'
    resource_type = 'PARAMS'
    chunk_number = '0'
    chunk_size = '1'

    global evnfm_param_resource_id

    evnfm_param_resource_id = upload_node_product_resources(resource_file_path, resource_name, resource_type, evnfm_vendor_product_id,
                                  chunk_number, chunk_size)


def get_EVNFM_val_stream_val_level_id():
    global evnfm_val_level_id

    global evnfm_val_stream_id

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
    name = 'AUTO_ECDE_EVNFM_VALIDATION_PROFILE'
    evnfm_val_level_id =  get_validation_id(connection,ecde_fqdn,auth_basic)
    evnfm_val_stream_id = get_validation_profile_id(connection,ecde_fqdn,auth_basic,name)

    connection.close()



def validate_EVNFM_dummy_vendor_product():
    log.info('Start validating the product for dummy node')

    file_name = 'ecde_validate_product.json'

    resources_id_list = [{"id":evnfm_image_resource_id}, {"id":evnfm_param_resource_id}]

    update_validate_product_file(file_name, evnfm_vendor_product_id, resources_id_list, evnfm_val_level_id,
                                 evnfm_val_stream_id,evnfm_vnf_type_id,evnfm_vendor_id)

    validate_node_vendor_product('EVNFM-DUMMY', file_name, evnfm_vendor_product_id)

    log.info('Finished validating the product for dummy node')


def verify_EVNFM_dummy_validation_order():

    get_validation_order_id_status('EVNFM-DUMMY', 3600)


