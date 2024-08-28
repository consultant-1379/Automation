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
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import time 
import random
import ast
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_DEPLOYMENT import *

log = Logger.get_logger('ECDE_NODE_PREREQUISITES.py')



def create_dummy_node_vnf_type():
    """
    we can use same vnf type for multiple application (EVNFM, ECM )
    Keeping it as generic and will return the id
    """
    try:
        log.info('Start creating the VNF type')
        Report_file.add_line('Start creating the VNF type')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_vnf_type.json'
        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/v-nf-types' -d @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '201 Created' in command_output:
            log.info(f'vnf type has been created sucessfully')
            Report_file.add_line(f'vnf type has been created sucessfully ')
        elif 'error.recordWithSameName' in command_output:
            log.info(f'vnf type is already exists ')
            Report_file.add_line(f'vnf type is already exist ')
        else:
            log.error('Error creating vnf type with output  %s' , command_output)
            Report_file.add_line('Error creating vnf type with output  ' + command_output)
            assert False

        vnf_type_id = get_vnf_type_id(connection, ecde_fqdn, auth_basic)

        return vnf_type_id

    except Exception as e:
        log.error('Error creating vnf-type with exception mesg %s',  str(e))
        Report_file.add_line('Error creating vnf-type with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()


def create_dummy_node_validation_level():
    """
    we can use same validation level  for multiple application (EVNFM, ECM )
    Keeping it as generic and will return the id
    """
    try:
        log.info('Start creating the validation level')
        Report_file.add_line('Start creating the validation level')
        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        file_name = 'create_validation_level.json'
        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/validation-levels' -d @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        if '201 Created' in command_output:
            log.info(f'validation level has been created sucessfully')
            Report_file.add_line(f'validation level has been created sucessfully ')
        elif 'error.recordWithSameName' in command_output:
            log.info(f'validation level is already exists ')
            Report_file.add_line(f'validation level is already exists ')
        else:
            log.error('Error creating validation level with output  %s',  command_output)
            Report_file.add_line('Error creating validation level with output  ' + command_output)
            assert False

        val_level_id = get_validation_id(connection, ecde_fqdn, auth_basic)

        return val_level_id

    except Exception as e:
        log.error('Error creating validation level with exception mesg %s' , str(e))
        Report_file.add_line('Error creating validation level with exception mesg ' + str(e))
        assert False

    finally:
        connection.close()


def change_ecde_password_first_login(user):
    try:
        log.info(f'Start updating the ecde {user} password ')
        Report_file.add_line(f'Start updating the ecde {user} password ')


        ecde_fqdn ,ecde_user, ecde_password = Server_details.ecde_user_details(Server_details,user)


        ecm_server_ip,ecm_username,ecm_password = Server_details.ecm_host_blade_details(Server_details)


        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        data = '"newPassword":{}'.format('"'+ecde_password+'"')

        if 'admin' == user:
            ecde_default_password = 'admin'
        else:
            ecde_default_password = ecde_password

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_default_password)

        command = '''curl -X POST --insecure --header 'Authorization:Basic {}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{}/core/api/reset_password/force' -d '{}{}'''.format(auth_basic,ecde_fqdn,'{'+data+'}',"'")
        Report_file.add_line('command to update admin password  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        if output['activated'] == True:
            log.info(f'Finished updating the ecde {user} password ')
            Report_file.add_line(f'Finished updating the ecde {user} password ')
        else:
            log.error('Something wrong while updating the password , please check the Report file for command output')
            assert False

    except Exception as e:
        log.error(f'Error updating the ecde {user} password  ' + str(e))
        Report_file.add_line(f'Error updating the ecde {user} password ')
        assert False

    finally:
        connection.close()


def update_standalone_conf_ecde():
    
    try:
        log.info('Start updating the ecde heap size for big resource upload')
        Report_file.add_line('Start updating the ecde heap size for big resource upload')
        
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        
        ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
        
        vendor_ip = ecde_data._Ecde__ecde_vendor_ip

        file_name = 'standalone.conf'
        
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, r'/root/' + file_name)
        
        connection.close()
        
        log.info('Start performing steps on ECDE vendor')
        
        connection = ServerConnection.get_connection_with_file(vendor_ip, 'cloud-user', r'com_ericsson_do_auto_integration_files/ECDE_files/ecde-eo-staging_testing_ECDE.pem')
        interact = connection.invoke_shell()
        
            
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        time.sleep(2)
        
        interact.send('su - ecde' + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        
        if 'Password' in buff:
            interact.send('ecde' + '\n')
            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
        
        
        if  'UNIX password' in buff:
            interact.send('ecde' + '\n')
            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            
        if 'New password' in buff:
            interact.send('EricssonAthlone@123' + '\n')
            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            
        if 'Retype new password' in buff:
            interact.send('EricssonAthlone@123' + '\n')
            time.sleep(4)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            
        
        
        interact.send('cd $JBOSS_HOME/bin' + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        
        
        log.info('getting updated standalone.conf file from ECM host blade server')
        
        interact.send('scp root@{}:/root/standalone.conf standalone.conf'.format(ecm_server_ip) + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        
        if 'continue connecting' in buff:
            interact.send('yes' + '\n')
            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
        
        if 'password' in buff:
            interact.send(ecm_password + '\n')
            time.sleep(2)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            
        
        log.info('going to kill jboss process')
            
        interact.send("pgrep -f jboss-modules.jar" + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        
        list_data = buff.split('\\r\\n')
        log.info('jboss process Id : '+list_data[1])
        
        interact.send('kill -9 '+list_data[1] + '\n')
        time.sleep(20)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        
        log.info('Re-starting jboss server')
        
            
        interact.send('sudo -u ecde nohup $JBOSS_HOME/bin/standalone.sh -b 0.0.0.0 >> /var/log/ecde/jboss_start_'+str(random.randint(0,999))+'.log &\n')
        time.sleep(4)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        log.info('waiting 120 seconds to jboss server to come up')
        time.sleep(120)
        
        
        interact.shutdown(2)
        
        
        log.info('Finished updating the ecde heap size for big resource upload')
        Report_file.add_line('Finished updating the ecde heap size for big resource upload')
    except Exception as e:
        log.error('Error updating the ecde heap size for big resource upload '+str(e))
        Report_file.add_line('Error updating the ecde heap size for big resource upload')
        assert False

    finally:
        connection.close()


def create_onboarding_system(node_name,file_name,update = False):
    
    try:
    
        log.info('Start create-update the onboarding system for {}'.format(node_name))
        Report_file.add_line('Start creating the onboarding system for {}'.format(node_name))

        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        
        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name, r'/root/' + file_name)
        
        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)
        
        if update:
            command = '''curl -i -X PUT --insecure --header 'Authorization:Basic {}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{}/core/api/on-boarding-systems' -d @{}'''.format(auth_basic, ecde_fqdn,file_name)
            log.info('command to update onboarding system '+command)
            Report_file.add_line('command to update onboarding system   ' + command)
        else:
                
            command = '''curl -i -X POST --insecure --header 'Authorization:Basic {}' --header 'Content-Type: application/json' --header 'Accept: application/json'  'https://{}/core/api/on-boarding-systems' -d @{}'''.format(auth_basic, ecde_fqdn,file_name)
            log.info('command to create onboarding system '+command)
            Report_file.add_line('command to create onboarding system   ' + command)
        
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
                
        log.info('Finished create-update the onboarding system for {}'.format(node_name))
        Report_file.add_line('Finished create-update the onboarding system for {}'.format(node_name))
        
    except Exception as e:
        log.error('Error create-update the onboarding system for {} with error {}'.format(node_name,str(e)))
        Report_file.add_line('Error create-update the onboarding system for {} with error {}'.format(node_name, str(e)))
        assert False

    finally:
        connection.close()



# This method is to check the record in table 
# If record not exists then insert into the table
# It is using MYSQL_DB file from utilities 

def db_check_insert_activities(entity_name,node_name,table_name,column_name,record_name,column_string,values_tuple):
    
    try:
        
        log.info('Start creating {} for node {}'.format(entity_name,node_name))
        Report_file.add_line('Start creating {} for node {}'.format(entity_name, node_name))

        ecde_db_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
        ecde_db_ip = ecde_db_data._Ecde__ecde_db_ipaddress
        ecde_db_username = ecde_db_data._Ecde__ecde_db_username
        ecde_db_password = ecde_db_data._Ecde__ecde_db_password

        db_connection = get_mySQL_connection(ecde_db_ip, 'ECDEDB', ecde_db_username, ecde_db_password)
        
        record_exists = check_record_exits_mySQL_table(db_connection, table_name, column_name, record_name)
        
        if record_exists:
            log.info('{} already exist for node {}'.format(entity_name,node_name))
            Report_file.add_line('{} already exist for node {}'.format(entity_name, node_name))
        
        else:
            insert_data_mySQL_table(db_connection, table_name, column_string, values_tuple)
            log.info('Finished creating {} for node {}'.format(entity_name,node_name))
            Report_file.add_line('Finished creating {} for node {}'.format(entity_name, node_name))
        
        

    except Exception as e:
        
        log.error('Error creating {} for node with error message : {}'.format(entity_name,str(e)))
        Report_file.add_line('Error creating {} for node with error message : {}'.format(entity_name, str(e)))
        assert False

    finally:
        db_connection.close()
        
        
def db_check_record_exists(entity_name,node_name,table_name,column_name,record_name):
    
     
    try:
        
        log.info('Checking record  {} for node {}'.format(entity_name,node_name))
        Report_file.add_line('Checking record  {} for node {}'.format(entity_name, node_name))

        ecde_db_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
        ecde_db_ip = ecde_db_data._Ecde__ecde_db_ipaddress
        ecde_db_username = ecde_db_data._Ecde__ecde_db_username
        ecde_db_password = ecde_db_data._Ecde__ecde_db_password

        db_connection = get_mySQL_connection(ecde_db_ip, 'ECDEDB', ecde_db_username, ecde_db_password)
        
        record_exists = check_record_exits_mySQL_table(db_connection, table_name, column_name, record_name)
        
        if record_exists:
            return True
        
        else:
            return False
            

    except Exception as e:
        
        log.error('Error Checking record {} for node with error message : {}'.format(entity_name,str(e)))
        Report_file.add_line('Error Checking record {} for node with error message : {}'.format(entity_name, str(e)))
        assert False

    finally:
        db_connection.close()



def db_insert_activities(entity_name,node_name,table_name,column_string,values_tuple):
    
    try:
        
        log.info('Start creating {} for node {}'.format(entity_name,node_name))
        Report_file.add_line('Start creating {} for node {}'.format(entity_name, node_name))

        ecde_db_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
        ecde_db_ip = ecde_db_data._Ecde__ecde_db_ipaddress
        ecde_db_username = ecde_db_data._Ecde__ecde_db_username
        ecde_db_password = ecde_db_data._Ecde__ecde_db_password

        db_connection = get_mySQL_connection(ecde_db_ip, 'ECDEDB', ecde_db_username, ecde_db_password)
        
        
        insert_data_mySQL_table(db_connection, table_name, column_string, values_tuple)
        log.info('Finished creating {} for node {}'.format(entity_name,node_name))
        Report_file.add_line('Finished creating {} for node {}'.format(entity_name, node_name))
        
        

    except Exception as e:
        
        log.error('Error creating {} for node with error message : {}'.format(entity_name,str(e)))
        Report_file.add_line('Error creating {} for node with error message : {}'.format(entity_name, str(e)))
        assert False

    finally:
        db_connection.close()        



def get_record_id(table_name,id_column_name,column_name,record_name):
    
    try:
        
        log.info('start fetching id for '+record_name)
        Report_file.add_line('start fetching id for ' + record_name)

        ecde_db_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
        ecde_db_ip = ecde_db_data._Ecde__ecde_db_ipaddress
        ecde_db_username = ecde_db_data._Ecde__ecde_db_username
        ecde_db_password = ecde_db_data._Ecde__ecde_db_password

        db_connection = get_mySQL_connection(ecde_db_ip, 'ECDEDB', ecde_db_username, ecde_db_password)
        
        record_id = get_record_id_from_mySQL_table(db_connection, table_name, id_column_name, column_name, record_name)
        
        log.info('Id for record name {} in table {} is {}'.format(record_name,table_name,str(record_id)))
        
        return record_id
        
        
    except Exception as e:
        
        log.error('Error fetching id for {} | Error - {}'.format(record_name,str(e)))
        Report_file.add_line('Error fetching id for {} | Error - {}'.format(record_name, str(e)))
        assert False

    finally:
        db_connection.close()

def get_record_id_two_inputs(table_name,id_column_name,column_name,record_name,column_name2,record_value):
    
    try:
        
        log.info('start fetching id for '+record_name)
        Report_file.add_line('start fetching id for ' + record_name)

        ecde_db_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
        ecde_db_ip = ecde_db_data._Ecde__ecde_db_ipaddress
        ecde_db_username = ecde_db_data._Ecde__ecde_db_username
        ecde_db_password = ecde_db_data._Ecde__ecde_db_password

        db_connection = get_mySQL_connection(ecde_db_ip, 'ECDEDB', ecde_db_username, ecde_db_password)
        
        record_id = get_record_id_from_mySQL_two_inputs(db_connection, table_name, id_column_name, column_name, record_name, column_name2, record_value)
        log.info('Id for record name {} in table {} is {}'.format(record_name,table_name,str(record_id)))
        
        return record_id
        
        
    except Exception as e:
        
        log.error('Error fetching id for {} | Error - {}'.format(record_name,str(e)))
        Report_file.add_line('Error fetching id for {} | Error - {}'.format(record_name, str(e)))
        assert False

    finally:
        db_connection.close()

def create_node_vnf_type(node_name,table_name,column_name,record_name,column_string,values_tuple):
    
    db_check_insert_activities('VNF_TYPE', node_name, table_name, column_name, record_name, column_string, values_tuple)
    
    
def create_node_validation_level(node_name,table_name,column_name,record_name,column_string,values_tuple): 
    
    db_check_insert_activities('Validation-level', node_name, table_name, column_name, record_name, column_string, values_tuple)
    
       
def create_deploy_type_validation_stream(node_name,table_name,column_name,record_name,column_string,values_tuple):
    
    db_check_insert_activities('Validation-stream', node_name, table_name, column_name, record_name, column_string, values_tuple)
    
          
        
def assign_vnf_type_val_level_to_val_stream(node_name,table_name,column_name,record_name,column_string,values_tuple):
    
    db_check_insert_activities('assign_vnf_type_val_level_to_val_stream', node_name, table_name, column_name, record_name, column_string, values_tuple) 
             
        
        
def create_deploy_type_test_env_profile(node_name, file_name,name):
    try:

        log.info(f'Start creating TEP for {node_name}')
        Report_file.add_line(f'Start creating TEP for {node_name}')

        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(connection,
                                        r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                        r'/root/' + file_name)

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)



        command = '''curl -i -X POST --insecure --header 'Authorization:Basic {}' --header 'Content-Type: multipart/form-data'  --header 'Accept: application/json'  {} -F 'fileSource=@{}' 'https://{}/core/api/orchestrator/pipeline/upload{}'''.format(auth_basic,'{"type":"formData"}',file_name,ecde_fqdn,"'")

        log.info('command :' + command)
        Report_file.add_line('command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)


        if '200 OK' in command_output:
            log.info('Finished create TEP for {}'.format(node_name))
            Report_file.add_line('Finished create TEP for {}'.format(node_name))
        elif 'TEP name already exists' in command_output:
            log.info('TEP name already exists {}'.format(node_name))
            Report_file.add_line('TEP name already exists {}'.format(node_name))
        else:
            log.error('Error creating TEP with output '+command_output)
            Report_file.add_line('Error creating TEP with output , check the above comamnd output for details  ')
            assert False
        return get_test_env_profile_id(connection, ecde_fqdn, auth_basic,name)

    except Exception as e:
        log.error('Error create TEP for {} with error {}'.format(node_name, str(e)))
        Report_file.add_line('Error create TEP for {} with error {}'.format(node_name, str(e)))
        assert False

    finally:
        connection.close()
    
    
def create_node_vendor(node_name, table_name, column_name, record_name, column_string, values_tuple):
    
    db_check_insert_activities('Vendor', node_name, table_name, column_name, record_name, column_string, values_tuple)
    
    
def create_node_vendor_user(node_name, table_name, column_name, record_name, column_string, values_tuple):
    
    db_check_insert_activities('user', node_name, table_name, column_name, record_name, column_string, values_tuple)   
     
    
def assign_vnf_type_val_stream_to_vendor(node_name, table_name, column_name, record_name, column_string, values_tuple):
    
    db_check_insert_activities('assign_vnf_type_val_stream_to_vendor', node_name, table_name, column_name, record_name, column_string, values_tuple) 
    
    
def create_deploy_type_validation_track(node_name, table_name, column_name, record_name, column_string, values_tuple): 
    
    db_check_insert_activities('Vendor-Specific Validation Tracks', node_name, table_name, column_name, record_name, column_string, values_tuple) 
        


def get_vendor_id(connection,ecde_fqdn,auth_basic):

    item = "vendorName"
    name = "AUTO_VENDOR"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/vendors" '''
    return get_item_id_with_name(connection, command, item, name)


def get_AAT_tool_id(connection,ecde_fqdn,auth_basic):

    item = "testHeadName"
    name = "AAT"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/test-head-catalogs" '''
    return get_item_id_with_name(connection, command, item, name)

def get_AAT_testcase_id(connection,ecde_fqdn,auth_basic):

    item = "testCaseName"
    name = "ping_self"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/testcases" '''
    return get_item_id_with_name(connection, command, item, name)

def get_vnf_type_id(connection,ecde_fqdn,auth_basic,name = "AUTO_DUMMY"):

    item = "vnfName"
    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/v-nf-types" '''
    return get_item_id_with_name(connection, command, item, name)

def get_validation_id(connection, ecde_fqdn, auth_basic,name = "AUTO_INSTANTIATION"):

    item = "validationLevelName"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/validation-levels" '''
    return get_item_id_with_name(connection, command, item, name)


def get_validation_profile_id(connection, ecde_fqdn, auth_basic,name):
    item = "validationStreamName"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/validation-streams" '''
    return get_item_id_with_name(connection, command, item, name)



def get_onboarding_system_id(connection, ecde_fqdn, auth_basic,name,check_exists = False):
    item = "onBoardingSystemName"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/on-boarding-systems" '''
    return get_item_id_with_name(connection, command, item, name,check_exists)


def get_test_env_profile_id(connection, ecde_fqdn, auth_basic,name):
    item = "name"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/test-environment-files" '''
    return get_item_id_with_name(connection, command, item, name)


def get_validation_track_id(connection, ecde_fqdn, auth_basic, name):

    item = "validationStream"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/vendor-specific-validation-tracks" '''
    return get_item_id_with_name(connection, command, item, name)


def get_vendor_product_id(connection, ecde_fqdn, auth_basic, name):

    item = "productName"

    command = f'''curl -X GET --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json' --header 'Accept: application/json'  "https://{ecde_fqdn}/core/api/vnf-products" '''
    return get_item_id_with_name(connection, command, item, name)


