'''
Created on Apr 27, 2020
corona times
@author: emaidns
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.ECDE_DUMMY_ECM_DEPLOYMENT import *
import time

log = Logger.get_logger('ECDE_CDD_NODE_DEPLOYMENT.py')


def get_ccd_node_prerequisite():
    try:

        log.info('Start populating the already created TEP , vnf type ,validation level and validation profile')
        Report_file.add_line('Start fretching the already created TEP , vnf type ,validation level and validation profile')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'ecde_cdd_prereq.json'
        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i --insecure --location --request POST 'https://{ecde_fqdn}/core/v1/integrations/notify' --header 'Content-Type: application/json' -d  @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '202 Accepted' in command_output:
            log.info(f'Step successfull . TEP ,vnf type, validation and profile has been populated to ECDE ')
            Report_file.add_line(f'Step successfull . TEP ,vnf type, validation and profile has been populated to ECDE ')
            log.info('waiting 60 seconds for all the ids to generate in ECDE DB')
            time.sleep(60)
        else:
            log.error('Error while populating the TEP ,vnf type , profile and level with output  ' + command_output)
            Report_file.add_line('Error while populating the TEP ,vnf type , profile and level with output  ' + command_output)
            assert False


    except Exception as e:
        log.error('Error while populating the TEP ,vnf type , profile and level with exception mesg ' + str(e))
        Report_file.add_line('Error while populating the TEP ,vnf type , profile and level with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()




def create_CDD_NODE_validation_track():
    try:
        log.info('Start creating the CDD NODE  validation track')
        Report_file.add_line('Start creating the CDD NODE validation track')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_track.json'

        # all pre-req have same name of entry --- need to update here

        name = 'dummy_test_product_T-123456'
        global vendor_id

        vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

        global vnf_type_id

        vnf_type_id = get_vnf_type_id(connection, ecde_fqdn, auth_basic,name)

        global val_level_id

        val_level_id = get_validation_id(connection, ecde_fqdn, auth_basic,name)

        global val_profile_id

        val_profile_id = get_validation_profile_id(connection, ecde_fqdn, auth_basic,name)

        global cdd_test_env_profile_id

        cdd_test_env_profile_id = get_test_env_profile_id(connection,ecde_fqdn,auth_basic,name)


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

        global val_track_id
        val_track_id = get_validation_track_id(connection, ecde_fqdn, auth_basic, name)

    except Exception as e:
        log.error('Error creating validation track with exception mesg ' + str(e))
        Report_file.add_line('Error creating validation track with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()


def assign_CDD_NODE_validation_track():
    try:
        log.info('Start assigning the CDD NODE  validation track to TEP')
        Report_file.add_line('Start assigning the CDD NODE  validation track to TEP')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_track.json'
        ### profile name has to upadate
        update_assign_validation_track_file(file_name,vendor_id, vnf_type_id,val_level_id,val_profile_id,'dummy_test_product_T-123456',val_track_id,cdd_test_env_profile_id)

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




def create_CDD_NODE_product():
    log.info('Start Creating product for CDD NODE deployment')

    # Every time product name must be different

    vendor_fqdn, vendor_user, vendor_password = Server_details.ecde_user_details(Server_details, 'vendor')

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
    vendor_auth_basic = Common_utilities.get_auth_basic(Common_utilities, vendor_user, vendor_password)

    global cdd_vendor_id
    cdd_vendor_id = get_vendor_id(connection,ecde_fqdn,auth_basic)

    node_name = 'CDD_NODE'
    product_name = Common_utilities.get_name_with_timestamp(Common_utilities, 'ECDE_CDD_NODE')

    file_name = 'create_ecde_product.json'

    name = 'dummy_test_product_T-123456'
    global cdd_vnf_type_id
    cdd_vnf_type_id = get_vnf_type_id(connection,ecde_fqdn,auth_basic,name)

    update_product_file(file_name, product_name, "CDD_NODE", cdd_vnf_type_id, "AUTO_VENDOR",cdd_vendor_id)
    create_node_vendor_product(connection, vendor_auth_basic ,node_name, file_name)

    global cdd_vendor_product_id

    cdd_vendor_product_id = get_vendor_product_id(connection, ecde_fqdn, vendor_auth_basic, product_name)

    log.info('Finished Creating product for CDD NODE deployment')


def get_CDD_val_stream_val_level_id():
    global cdd_val_level_id

    global cdd_val_stream_id

    ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

    name = 'dummy_test_product_T-123456'
    cdd_val_level_id =  get_validation_id(connection,ecde_fqdn,auth_basic,name)
    cdd_val_stream_id = get_validation_profile_id(connection,ecde_fqdn,auth_basic,name)

    connection.close()



def validate_CDD_NODE_vendor_product():
    log.info('Start validating the product for dummy node')

    file_name = 'ecde_validate_product.json'

    resources_id_list = []

    update_validate_product_file(file_name, cdd_vendor_product_id, resources_id_list, cdd_val_level_id,
                                 cdd_val_stream_id,cdd_vnf_type_id,cdd_vendor_id)

    validate_node_vendor_product('CDD-NODE', file_name, cdd_vendor_product_id)

    log.info('Finished validating the product for CDD node')


def verify_CDD_NODE_validation_order():

    get_validation_order_id_status('CDD-NODE', 3600)


