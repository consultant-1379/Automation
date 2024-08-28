
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import ast

log = Logger.get_logger('SO_POST_INSTALLATION')


def check_tenant_user_exists(connection,command,name):
    
    log.info ('Check '+name+ ' exists or not ')
    Report_file.add_line('Check ' + name + ' exists')
    
    Report_file.add_line('command : ' + command)
    
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
   

    if command_out:
        output = ast.literal_eval(command_out)
    
    
        for block in output:
            
            if name in block.values():

                log.info(name +' already exist')
                return True
    
    log.info(name +' does not exist')        
    return False


def create_so_tenant():

    try:
        
    
        log.info('Start So tenant creation')
        Report_file.add_line('Start So tenant creation')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        global so_host_name    
        so_host_name = sit_data._SIT__so_host_name 
        
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
            
        
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
    
    
    
        if so_deployment_type == 'IPV6':
            
            log.info('SO Deployment type is IPV6, connecting with open stack ' )
            connection = ServerConnection.get_connection(openstack_ip, username, password)
            
        else:
        
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            
        user = 'so-user'    
        password = 'Ericsson123!'
        tenant = 'master'
        
        master_so_token = Common_utilities.generate_so_token(Common_utilities,connection,so_host_name,user,password,tenant)  
        
        command ='''curl --insecure -X  GET -H 'Cookie: JSESSIONID="{}"' https://{}/idm/tenantmgmt/v1/tenants'''.format(master_so_token,so_host_name)
        
        exists = check_tenant_user_exists(connection,command,'staging-tenant')
            
        if not exists:
            
            log.info('Creating SO Tenant as staging-tenant ')
            Report_file.add_line('Creating SO Tenant as staging-tenant')
            file_name = 'createStagingTenant.json'
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            command ='''curl --insecure -X  POST -H "Content-Type: application/json" -H 'Cookie: JSESSIONID="{}"' --data @createStagingTenant.json  https://{}/idm/tenantmgmt/v1/tenants'''.format(master_so_token,so_host_name)
            log.info ('create so tenant '+command)
            Report_file.add_line('create so tenant ' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            Report_file.add_line('create so tenant output ' + command_output)
              
    except Exception as e:
        
        log.error('Error So tenant creation  '+str(e))
        Report_file.add_line('Error So tenant creation ' + str(e))
        assert False                        
    finally:
        connection.close() 


def verify_user(command_output):
    try:
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)


        if command_out:
            output = ast.literal_eval(command_out)
            
            if 'ENABLED' == output['status']:
                Report_file.add_line('user created successfully')
                log.info('user created successfully')
                
            else:
                raise ValueError('Unexpected output. Please check the Report file ')
            
        else:
            raise ValueError('User creation Command output is empty ')
        
        
        
    except Exception as e:
        log.error('Error So user creation  '+str(e))
        Report_file.add_line('Error So user creation ' + str(e))
        assert False    
        
def create_user_tenant_admin_role():
    try:
        log.info('Creating Tenant admin user as tenant-admin-user ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
    
    
    
        if so_deployment_type == 'IPV6':
            
            log.info('SO Deployment type is IPV6, connecting with open stack ' )
            connection = ServerConnection.get_connection(openstack_ip, username, password)
            
        else:        
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        
        user = 'so-user'    
        password = 'Ericsson123!'
        tenant = 'master'
    
        master_so_token = Common_utilities.generate_so_token(Common_utilities,connection,so_host_name,user,password,tenant)
        command ='''curl --insecure -X  GET -H 'Cookie: JSESSIONID="{}"' 'https://{}/idm/usermgmt/v1/users?search=(tenantname==staging-tenant){}'''.format(master_so_token,so_host_name,"'")
        
        exists = check_tenant_user_exists(connection,command,'tenant-admin-user')
            
        if not exists:
        
            Report_file.add_line('Creating Tenant admin user as tenant-admin-user')

            file_name = 'createAdminUser.json'            
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            
            command ='''curl --insecure -X  POST -H "Content-Type: application/json" -H 'Cookie: JSESSIONID="{}"' --data @createAdminUser.json  https://{}/idm/usermgmt/v1/users'''.format(master_so_token,so_host_name)
            log.info ('create tenant-admin-user '+command)
            Report_file.add_line('create tenant-admin-user ' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            Report_file.add_line('create tenant-admin-user output ' + command_output)
            
            verify_user(command_output)
            
    except Exception as e:
        
        log.error('Error So Tenant admin user creation  '+str(e))
        Report_file.add_line('Error So Tenant admin user creation ' + str(e))
        assert False                        
    finally:
        connection.close() 
    
def create_user_so_designer_role():
    
    try:
        log.info('Creating staging-user with SO Designer Role ')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
    
        if so_deployment_type == 'IPV6':
            
            log.info('SO Deployment type is IPV6, connecting with open stack ' )
            connection = ServerConnection.get_connection(openstack_ip, username, password)
            
        else:        
        
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        
        user = 'tenant-admin-user'    
        password = 'Testing12345!!'
        tenant = 'staging-tenant'
    
        admin_so_token = Common_utilities.generate_so_token(Common_utilities,connection,so_host_name,user,password,tenant)        
    
        command ='''curl --insecure -X  GET -H 'Cookie: JSESSIONID="{}"' https://{}/idm/usermgmt/v1/users'''.format(admin_so_token,so_host_name)
        
        exists = check_tenant_user_exists(connection,command,'staging-user')
            
        if not exists:
        
            
            Report_file.add_line('Creating staging-user with SO Designer Role')
            
            file_name = 'createStagingUser.json'            
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            
            command ='''curl --insecure -X  POST -H "Content-Type: application/json" -H 'Cookie: JSESSIONID="{}"' --data @createStagingUser.json https://{}/idm/usermgmt/v1/users'''.format(admin_so_token,so_host_name)
            log.info ('create staging-user with SO Designer Role  '+command)
            Report_file.add_line('create staging-user with SO Designer Role ' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            Report_file.add_line('create staging-user with SO Designer Role output ' + command_output)
            
            verify_user(command_output)
            
    except Exception as e:
        
        log.error('Error create staging-user with SO Designer Role   '+str(e))
        Report_file.add_line('Error create staging-user with SO Designer Role   ' + str(e))
        assert False                        
    finally:
        connection.close()