'''
Created on Sep 27, 2019

@author: emaidns
'''



from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.MYSQL_DB import *
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import ast
import time
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details



log = Logger.get_logger('ECDE_NODE_DEPLOYMENT.py')


validation_order_id = ''


def create_node_vendor_product(connection, auth_basic,node_name, file_name):
    try:
        log.info('Start creating the vendor_product for {}'.format(node_name))
        Report_file.add_line('Start creating the vendor_product for {}'.format(node_name))
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'vendor')
        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/vnf-products' -d @{file_name}'''

        log.info('curl command : ' + command)
        Report_file.add_line('curl command : ' + command)


        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('command output : ' + command_output)

        if '201 Created' in command_output:
            log.info('Finished creating the vendor_product for {}'.format(node_name))
            Report_file.add_line('Finished creating the vendor_product for {}'.format(node_name))

        else:
            log.error('Error in curl creating the vendor_product ' + command_output)
            Report_file.add_line('Error in curl creating the vendor_product ' + command_output)
            assert False

    except Exception as e:
        log.error('Error creating the vendor_product  for {} with error {}'.format(node_name, str(e)))
        Report_file.add_line('Error creating the vendor_product  for {} with error {}'.format(node_name, str(e)))
        assert False



def upload_node_product_resources(resource_file_path,resource_name,resource_type,vendor_product_id,chunk_number,chunk_size):
    
    # resource_name : it is file name that needs to be upload on product
    
    try:
        
        log.info('Start uploading the resource {} with type {} for to vendor_product id {}'.format(resource_name,resource_type,vendor_product_id))
        Report_file.add_line('Start uploading the resource {} with type {} for to vendor_product id {}'.format(resource_name, resource_type, vendor_product_id))

        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'vendor')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        
        log.info('start fetching the total size of resource '+resource_name)
        
        command = '''wc -c {} | awk {}'''.format(resource_file_path,"'{print $1}'")
        
        stdin, stdout, stderr = connection.exec_command(command)
        
        command_output = str(stdout.read())
        Report_file.add_line('command output : ' + command_output)
        
        total_size = command_output[2:-3:1]
        form_data = '{"type":"formData"}'
        
        command =  f'''curl -X POST --insecure  --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: multipart/form-data' --header 'Accept: application/json' {form_data} -F 'resourceFileName=@{resource_file_path}' 'https://{ecde_fqdn}/core/api/product-resources/upload?_chunkSize={total_size}&_currentChunkSize={chunk_size}&_chunkNumber={chunk_number}&_totalSize={total_size}&resourceName={resource_name}&description=auto_eo-stagging&resourceType={resource_type}&vnfProductId={vendor_product_id}{"'"}'''
        
        Report_file.add_line('curl command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        
        if 'id' in str(output):
            log.info('Finished uploading the resource {} with type {} for to vendor_product id {}'.format(resource_name,resource_type,vendor_product_id))
            Report_file.add_line('Finished uploading the resource {} with type {} for to vendor_product id {}'.format(resource_name, resource_type, vendor_product_id))
            resource_id = output['id']
            log.info('Resource id is : '+str(resource_id))
            Report_file.add_line('Resource id is : ' + str(resource_id))
            return resource_id
        else:
            log.error('Error in curl uploading the vendor_product resources '+ command_output)
            Report_file.add_line('Error in curl uploading the vendor_product resources ' + command_output)
            assert False
        
        
    except Exception as e:
        log.error('Error uploading the resource {} with type {} for to vendor_product id {} ERROR : {} '.format(resource_name,resource_type,vendor_product_id,str(e)))
        Report_file.add_line(
            'Error uploading the resource {} with type {} for to vendor_product id {} ERROR : {} '.format(resource_name, resource_type, vendor_product_id, str(e)))
        assert False

    finally:
        connection.close()


def validate_node_vendor_product(node_name, file_name, product_id):
    try:

        log.info('Start validating the vendor_product id {} for node type {}'.format(product_id, node_name))
        Report_file.add_line('Start validating the vendor_product id {} for node type {}'.format(product_id, node_name))

        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'vendor')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'Authorization:Basic {}' -d @{} 'https://{}/core/api/validationorders-and-mapping{}'''.format(
            auth_basic, file_name, ecde_fqdn, "'")

        Report_file.add_line('curl command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        if 'id' in str(output):
            global validation_order_id
            validation_order_id = output['id']
            log.info('Validation order id is : ' + str(validation_order_id))
            Report_file.add_line('Validation order id is : ' + str(validation_order_id))
            log.info('Finished validating the vendor_product id {} for node type {}'.format(product_id, node_name))
            Report_file.add_line('Finished validating the vendor_product id {} for node type {}'.format(product_id,
                                                                                                        node_name))

        else:
            log.error('Error in curl validating the vendor_product ' + command_output)
            Report_file.add_line('Error in curl validating the vendor_product ' + command_output)
            assert False


    except Exception as e:
        log.error(
            'Error validating the vendor_product id {} for node type {} with ERROR : {}'.format(product_id, node_name,
                                                                                                str(e)))
        Report_file.add_line('Error validating the vendor_product id {} for node type {} with ERROR : {}'.format(
                                 product_id, node_name, str(e)))
        assert False

    finally:
        connection.close()
        
    
    
def get_validation_order_id_status(node_name,timeout):  
    
    try:
    
        log.info('Start fetching the validation order status for validation order id {} and node type {}'.format(str(validation_order_id),node_name))
        Report_file.add_line('Start fetching the validation order status for validation order id {} and node type {}'.format(str(validation_order_id), node_name))
        
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'vendor')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
        
        command = f'''curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'Authorization:Basic {auth_basic}'  'https://{ecde_fqdn}/core/api/validation-order-test-case-mappings/from-OrderId/{validation_order_id}{"'"}'''
    
        log.info('Time out for this process is {} seconds '.format(str(timeout)))
        
        
        while(timeout !=0):
            
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            output = ast.literal_eval(command_out)

                
            order_status = output['orderStatus']
            if 'REJECTED' in order_status or 'CANCELLING' in order_status:
                log.error(
                    'Order status for order id {} is {} , Somthing wrong please check'.format(str(validation_order_id), order_status))
                Report_file.add_line('Order status for order id {} is {}'.format(str(validation_order_id),
                                                                                 order_status))
                log.error('Please check command output in Report file for more details ..')
                assert False

            elif 'QUEUED' in order_status or 'INPROGRESS' in order_status or 'SUBMITTED' in order_status:
                log.info(f'Order status is {order_status}')
                log.info('waiting 30 seconds to check the status again')
                timeout = timeout - 30
                time.sleep(30)

            elif 'WAITING' in order_status:
                log.info(f'Order status is {order_status} to start terminate of VNF')
                log.info('waiting 30 seconds to check the status again')
                timeout = timeout - 30
                time.sleep(30)

            elif 'COMPLETED' in order_status:
                log.info('Order status is COMPLETED , checking Validation status ')
                validation_status = output['validationStatus']
                if 'FAILED' in validation_status:
                    log.error('Validation status for order id {} is {}'.format(str(validation_order_id),
                                                                                     validation_status))
                    Report_file.add_line('Validation status for order id {} is {}'.format(
                        str(validation_order_id), validation_status))
                    log.error('Please check in ECDE for more details on failure , for comamnd output may check in Report file ')

                    assert False

                elif 'PASSED' in validation_status:
                    log.info('Validation status for order id {} is {}'.format(str(validation_order_id),
                                                                                    validation_status))
                    Report_file.add_line('Validation status for order id {} is {}'.format(
                        str(validation_order_id), validation_status))
                    log.info('Testcase succesfully completed ')
                    break

                    
            else:
                log.info('Unknown response in curl requestStatus '+command_output)
                log.info('Please check if somthing missed from output')
                assert False

        
        
        if timeout == 0:
            log.error(f'Time out in automation script after {timeout} seconds for Validation order status')
            Report_file.add_line(f'Time out in automation script after {timeout} seconds for Validation order status')
            assert False
        
    except Exception as e:
        log.error('Error fetching the validation order status for validation order id '+str(validation_order_id) + 'Error : '+str(e))
        Report_file.add_line('Error fetching the validation order status for validation order id ' + str(validation_order_id) + 'Error : ' + str(e))
        assert False

    finally:
        connection.close()


def check_nfvo_exists_in_Vnflcm(connection):
    
    try:
    
        log.info('Start checking if nvfo exists on VNFlCM')
        
        command = '''sudo -i vnflcm nfvo list --nfvoinuse'''
        
        Report_file.add_line(' command : ' + command)
        
        stdin, stdout, stderr = connection.exec_command(command,get_pty=True)
        
        command_output = str(stdout.read())[2:-1:1]
        
        Report_file.add_line('command output : ' + command_output)
        
        if 'No NFVO Found' in command_output:
            return False ,''
        
        else:
            base_url = command_output.split('|')[9]
            return True , base_url
        
    except Exception as e:
        log.error('Error checking  nfvo in VNFLCM  '+str(e))
        Report_file.add_line('Error  nfvo in VNFLCM  ' + str(e))
        assert False    


def check_remove_nfvo_in_Vnflcm():   
    
    try:
        log.info('Start checking and remove nfvo in VNFLCM ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')    
    
        vnf_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        vnf_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        vnf_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password 
        
        connection = ServerConnection.get_connection(vnf_server_ip, vnf_username, vnf_password)
        
        nfvo_exists , base_url = check_nfvo_exists_in_Vnflcm(connection)
        
        if nfvo_exists:
            log.info('Nfvo already exists in VNF-LCM , going to remove nfvo')
            Report_file.add_line('Nfvo already exists in VNF-LCM , going to remove nfvo')
            command = '''sudo -i vnflcm nfvo delete --baseurl {}'''.format(base_url) 
            
            Report_file.add_line(' command : ' + command)
            
            stdin, stdout, stderr = connection.exec_command(command,get_pty = True)

            command_output = str(stdout.read())[2:-1:1]
            
            Report_file.add_line('command output : ' + command_output)
    

            if 'NFVO deleted successfully' in command_output:
                log.info('Successfully removed nfvo in VNF-LCM')
                Report_file.add_line('Successfully removed nfvo in VNF-LCM')
    
            else:
                log.error('Error removing nfvo in VNF-LCM , please check command output') 
                Report_file.add_line('Error removing nfvo in VNF-LCM , please check command output')
                assert False 

        else:
            log.info('In use Nfvo does not exist in VNFLCM ') 
            Report_file.add_line('In use Nfvo does not exist in VNFLCM ')
    
    except Exception as e:
        log.error('Error checking and remove nfvo in VNFLCM  '+str(e))
        Report_file.add_line('Error checking and remove nfvo in VNFLCM  ' + str(e))
        assert False

    finally:
        connection.close()
        
        
def check_add_nfvo_in_Vnflcm():
    
    try:
        log.info('Start checking and add nfvo in VNFLCM ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')    
    
        vnf_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        vnf_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        vnf_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password 
        
        connection = ServerConnection.get_connection(vnf_server_ip, vnf_username, vnf_password)
        
        nfvo_exists , base_url = check_nfvo_exists_in_Vnflcm(connection)
        
        if not nfvo_exists:
            log.info('Nfvo not exists in VNF-LCM , going to add nfvo')
            Report_file.add_line('Nfvo not exists in VNF-LCM , going to add nfvo')
            file_name = 'nfvoconfig.json'
            update_nfvo_config_file(file_name,dynamic_vnflcm = True)
            
            ServerConnection.put_file_sftp(connection, file_name, '/home/cloud-user/' + file_name)
            
            command = 'sudo -i vnflcm nfvo add --file /home/cloud-user/nfvoconfig.json'
            
            Report_file.add_line(' command : ' + command)
            
            stdin, stdout, stderr = connection.exec_command(command,get_pty = True)

            command_output = str(stdout.read())[2:-1:1]
            
            Report_file.add_line('command output : ' + command_output)
    

            if 'NFVO addition successful' in command_output:
                log.info('Successfully added nfvo in VNF-LCM')
                Report_file.add_line('Successfully added nfvo in VNF-LCM')
    
            else:
                log.error('Error adding nfvo in VNF-LCM , please check command output') 
                Report_file.add_line('Error adding nfvo in VNF-LCM , please check command output')
                assert False 

        else:
            log.info('In use Nfvo exists in VNFLCM ') 
            Report_file.add_line('In use Nfvo exists in VNFLCM ')
    
    except Exception as e:
        log.error('Error checking and add nfvo in VNFLCM  '+str(e))
        Report_file.add_line('Error checking and add nfvo in VNFLCM  ' + str(e))
        assert False

    finally:
        connection.close()      
        
        
def get_node_val_stream_val_level_id(val_level_name , val_stream_name):
    
    log.info('Start fetching validation level id')
    
    table_name = 'AVOP_VALIDATION_LEVEL'
    column_name = 'VALIDATION_LEVEL_NAME'
    record_name = val_level_name
    
    id_column_name = 'VALIDATION_LEVEL_ID'
    
    
    val_level_id = get_record_id(table_name, id_column_name, column_name, record_name) 
    
    log.info('Finished fetching validation level id')
    
    log.info('Start fetching the validation stream id')
    
    table_name = 'AVOP_VALIDATION_STREAM'
    column_name = 'VALIDATION_STREAM_NAME'
    record_name = val_stream_name
    
    id_column_name = 'VALIDATION_STREAM_ID'
    
    
    val_stream_id = get_record_id(table_name, id_column_name, column_name, record_name)   
    
    log.info('Finished fetching the validation stream id')         
    
    return val_level_id,val_stream_id








# Generic method to fetch out the id of any item if its name is available
# we know the name as we are only giving that while creation like AUTO_VENDOR, AUTO_USER
def get_item_id_with_name(connection,command,item,name,check_exists = False):

    """
      item -- it is key in output dict to fetch out the name to match with
     name -- name of the item that you already know
    """
    try:
        log.info(f'Start fetching out the id for {item} with value {name}')
        Report_file.add_line(f'Start fetching out the id for {item} with value {name}')

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)

        for data in output:
            attr_value = data[item]
            if name == attr_value:
                item_id = data['id']
                log.info(f'Id for {item} with name {name} is {item_id}')
                Report_file.add_line(f'Id for {item} with name {name} is {item_id}')
                return item_id

        if check_exists:
            log.info(f'Record for {item} with name {name} does not exists')
            Report_file.add_line(f'Record for {item} with name {name} does not exists')
            return False

        log.error(f'id for {item} with name {name} is NOT FOUND , Please check the ECDE if item created succesfully or not')
        Report_file.add_line(f'id for {item} with name {name} is NOT FOUND , Please check the ECDE if item created succesfully or not')
        assert False
    except Exception as e:
        log.error(f'Error fetching out the id for {item} with value {name} ERROR: '+str(e))
        Report_file.add_line(f'Error fetching out the id for {item} with value {name} ERROR: ' + str(e))
        assert False

