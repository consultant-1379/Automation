'''
Created on 15 Aug 2018


@author: emaidns
'''

from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
import ast
import time
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities import Integration_properties
from com_ericsson_do_auto_integration_scripts.PROJ_VIM import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import copy
from com_ericsson_do_auto_integration_model import Atlas

log = Logger.get_logger('VNF_LCM_ECM')


def main(not_enm = False):
    log.info('Starting script : Integration of VNF_LCM to ECM')
    
    execute_ECM_Steps(not_enm)
    execute_VNF_LCM_Steps(not_enm)
    vims_addition(not_enm)

def execute_json_file_data(json_file_data, file_name):
    Json_file_handler.update_json_file(Json_file_handler, file_name, json_file_data)


def ping_hostName(connection, hostName):
    cmd = 'ping -w 3 ' + hostName
    stdin, stdout, stderr = connection.exec_command(cmd)
    cmd_output = str(stdout.read())
    cmd_error = str(stderr.read())

    log.info('Pinging hostname  ' + hostName)
    Report_file.add_mesg('Pinging', 'hostname', hostName)

    if cmd_output:

        log.info('Ping response successful ' + cmd_output)
        Report_file.add_line('Ping response successful : ' + cmd_output)
        return True

    elif cmd_error:

        log.error('Ping response failed ' + cmd_error)
        Report_file.add_mesg('Verification Failed', 'Ping response failed ', cmd_output)
        return False


def verify_integration(connection):
    log.info(' Verification of Integration starts ')
    Report_file.add_line('Verification of Integration starts ')

    command = 'sudo -i /usr/local/bin/vnflcm vim list'
    stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

    data = stdout.read()
    string_data = data.decode("utf-8")
    log.info(string_data)

    if 'No data to display' in string_data:

        Report_file.add_mesg(' Vims not added ', ' Reason : ', string_data)
        log.error('Vims not added, Something went wrong please refer this data ' +string_data)
        connection.close()
        assert False

    elif string_data:
        response_list = []
        tokens1 = string_data.split('\n')
        string_data_length = len(tokens1)
        for x in range(3, string_data_length - 2):
            tokens2 = tokens1[x].split('|')
            tokens = [item.strip() for item in tokens2]
            vim_name = tokens[1]
            hostName = tokens[3]
            log.info('Pinging host name of ' + vim_name)
            response = ping_hostName(connection, hostName)
            response_list.append(response)
        
        if False in response_list:
            Report_file.add_mesg('Verification Failed', 'Please see above details for failure ',
                                 string_data)
            log.warn('Verification failed , Please see above logs for more details ')
            log.warn('Exiting script : Integration of VNF_LCM to ECM completed with failure ping response')

        else:
            Report_file.add_mesg('Verification Done', 'List of registered VIM ZONE  ', string_data)
            log.info('Verification Done List of registered VIM ZONE  ')
            log.info('Exiting script : Integration of VNF_LCM to ECM completed')


def execute_vims_addition(connection, command):
    log.info('Executing command : ' + command)
    stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
    data = stdout.read().decode("utf-8")

    Report_file.add_mesg('VIMS ADDITION', 'ON VNF-LCM SERVICE VM', data)
    log.info('Finished to execute command : ' + command)
    Report_file.add_line('Finished to execute vims addition ')


def execute_ECM_Steps(not_enm,test_hotel=False):
    # Login to the ECM host blade as root user using ssh
    log.info('Start executing ECM server steps ')
    Report_file.add_line('Start executing ECM server steps ')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    
    project_name = EPIS_data._EPIS__project_name
    
    
    vnf_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    vnf_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    
    if not_enm:
        vnf_server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
        
    else:
        vnf_server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
                           
        
    server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    enviornment = ecm_host_data._Ecm_core__enviornment
    data_file = r'com_ericsson_do_auto_integration_files/run_time_' + enviornment + '.json'
    connection = ServerConnection.get_connection(server_ip, username, password)
    
    log.info('updating  registerVnfm.json file  ')
    fileExists = ServerConnection.file_exists(server_ip, username, password,
                                               '/var/tmp/registerVnfm.json')
    if fileExists:
        command = ' cd /var/tmp/; cp registerVnfm.json registerVnfm.json.orig'
        stdin, stdout, stderr = connection.exec_command(command)
        Report_file.add_mesg('Step 1 ', 'Backup of registerVnfm.json done', command)

    
    vnfm_data = Initialization_script.get_model_objects(Initialization_script, 'VNFM')
    
    vnf_manager_name = vnfm_data._Vnfm__name
    file_name = 'registerVnfm.json'
    execute_json_file_data(vnfm_data.json_file_data, file_name)
    
    if not_enm:
        log.info('Going to update registerVnfm.json for without ENM Integration')
        endpoint_data = [{'name': Integration_properties.registervnfm_endpoints_name, 'ipAddress' : vnf_server_ip  ,'port' : 80, 'testUri' : '/' }]
        security_config_data = {'securityType':'HTTP'}
        attribute_dict = {'vendor':project_name,'endpoints':endpoint_data,'defaultSecurityConfig':security_config_data,'authIpAddress':vnf_server_ip,'authPort':80,'authPath':'/auth.json','authUserName':'vnfuser','authPassword':'passw0rd','authType':'BASIC'}
        Json_file_handler.modify_list_of_attributes(Json_file_handler, file_name,attribute_dict )
            
    
    sftp = connection.open_sftp()
    sftp.put(file_name, '/var/tmp/registerVnfm.json')
    sftp.close()

    Report_file.add_mesg('Step 2 ', 'updated registerVnfm.json', str(vnfm_data.json_file_data))
    log.info('updated  registerVnfm.json file  ')

    
    log.info('Generating token in the host blade server using the  curl command  ')
    
    if test_hotel:
        
        token = Common_utilities.authToken(Common_utilities,connection,core_vm_ip,is_ecm=True)
    
    else:
            
        token = Common_utilities.authToken(Common_utilities,connection,core_vm_ip) 
    
    log.info('Register VNFM with curl command  ')
    curl = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'AuthToken:{}' --data @registerVnfm.json 'https://{}/ecm_service/vnfms{}'''.format(
        token, core_vm_hostname, "'")
    command = 'cd /var/tmp/ ;' + curl

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    # subscription_id  = subscription_string['data']['vnfm']['id']
    output = ast.literal_eval(command_output[2:-1:1])
    requestStatus = output['status']['reqStatus']

    if 'SUCCESS' in requestStatus:
        subscription_string = ast.literal_eval(command_output[2:-1:1])
        if 'data' in subscription_string.keys():
            subscription_id = subscription_string['data']['vnfm']['id']
            log.info('got subscription id from server :' + subscription_id)
            Report_file.add_line('Subscription id : ' + subscription_id)
            
            dest = r'/root/' + 'run_time_' + enviornment + '.json'
            # Fetching file as parllel execution of dynamic and static LCM to update latest file on server.              
            ServerConnection.get_file_sftp(connection, dest, data_file)
            if not_enm:
                
                # Below attributes gets updated in case of VNF-LCM installed in Dynamic project 
                
                Json_file_handler.modify_attribute(Json_file_handler, data_file, 'DYNAMIC_VNF_MANAGER_ID', subscription_id)
                Json_file_handler.modify_attribute(Json_file_handler, data_file, 'DYNAMIC_VNF_MANAGER_NAME', vnf_manager_name)
                
            else:
                
                # Below attributes gets updated in case of VNF-LCM installed in static project
                
                Json_file_handler.modify_attribute(Json_file_handler, data_file, 'VNF_MANAGER_ID', subscription_id)
                Json_file_handler.modify_attribute(Json_file_handler, data_file, 'VNF_MANAGER_NAME', vnf_manager_name)
                
            
            ServerConnection.put_file_sftp(connection, data_file, dest)
    elif 'ERROR' in requestStatus:

        command_error = output['status']['msgs'][0]['msgText']

        log.error('Error executing curl command for registering the VNFM ' + command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for registering the VNFM')
        connection.close()
        assert False

    nfvo_data = Initialization_script.get_model_objects(Initialization_script, 'NFVO')

    nfvo_data.set_subscriptionId(nfvo_data, subscription_id)
    nfvo_data.json_file_data['subscriptionId'] = subscription_id

    connection.close()

    log.info('Finished executing ECM server steps ')
    Report_file.add_line('Finished executing ECM server steps ')


def get_cee_data_sync_proj(data):
    
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    
    vim_url = EPIS_data._EPIS__sync_vim_url
    adminUserName = EPIS_data._EPIS__existing_project_admin_username
    adminPassword = EPIS_data._EPIS__existing_project_admin_password
    sync_project_name = EPIS_data._EPIS__existing_project_name
    openrc_filename = EPIS_data._EPIS__sync_openrc_filename
    cloud_type = EPIS_data._EPIS__synccloudManagerType 
    cloud_hostname = EPIS_data._EPIS__sync_cloud_hostname  
    cloud_host_ip = EPIS_data._EPIS__sync_cloud_host_ip
    sync_project_id,sync_projectuser_id,sync_adminprojectuser_id= fetch_sync_proj_id(openrc_filename)    
    
    tenants = [{'name': sync_project_name, 'id' : sync_project_id , 'username' : adminUserName ,
                    'password' : adminPassword, 'defaultTenant' : 'True'}]
    
    
    block_attr = data
    block_data = copy.deepcopy(block_attr)

    block_data['name'] = sync_project_name 
    block_data['type'] = cloud_type
    block_data['defaultVim'] = 'False'
    block_data['hostIpAddress'] = cloud_host_ip
    block_data['hostName'] = cloud_hostname
    block_data['authUrl'] = vim_url
    block_data['tenants'] = tenants
    
    return block_data
    
    
def get_atlas_data_sync_proj(data):
    
    
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    
    adminUserName = EPIS_data._EPIS__existing_project_admin_username
    adminPassword = EPIS_data._EPIS__existing_project_admin_password
    cloud_type = EPIS_data._EPIS__synccloudManagerType
    sync_project_name = EPIS_data._EPIS__existing_project_name
    openrc_filename = EPIS_data._EPIS__sync_openrc_filename
    atlas_hostname = EPIS_data._EPIS__sync_atlas_hostname  
    atlas_host_ip = EPIS_data._EPIS__sync_atlas_host_ip
    auth_url = 'https://'+atlas_hostname+':443'
    sync_project_id,sync_projectuser_id,sync_adminprojectuser_id= fetch_sync_proj_id(openrc_filename)
    tenants = [{'name': sync_project_name, 'id' : sync_project_id , 'username' : adminUserName ,
                    'password' : adminPassword, 'defaultTenant' : 'True'}]
                                   
    block_attr = data
    block_data = copy.deepcopy(block_attr)

    block_data['name'] = 'sync_project_atlas'
    block_data['type'] = cloud_type
    block_data['defaultVim'] = 'False'
    block_data['hostIpAddress'] = atlas_host_ip
    block_data['hostName'] = atlas_hostname
    block_data['authUrl'] = auth_url
    block_data['tenants'] = tenants
    
    return block_data


def vim_File_Creation(connection):
    
    all_vim_data = []
    log.info('start working on all_vim templates.json file  ')
    cee_data = Initialization_script.get_model_objects(Initialization_script, 'CEE')

    all_vim_data.append(cee_data.json_file_data)

    Report_file.add_mesg('Step 3 ', 'data in cee_template_vim.json file   ', str(cee_data.json_file_data))

    atlas_data = Initialization_script.get_model_objects(Initialization_script, 'ATLAS')

    all_vim_data.append(atlas_data.json_file_data)

    Report_file.add_mesg('Step 4 ', 'data in atlas_template_vim.json file   ',
                         str(atlas_data.json_file_data))

    
    #Removing ECM data from All vim template as it is not needed any more.
    """ecm_data = Initialization_script.get_model_objects(Initialization_script, 'ECM')
    all_vim_data.append(ecm_data.json_file_data)
    Report_file.add_mesg(Report_file, 'Step 5 ', 'data in  ecm_template_vim.json file   ', str(ecm_data.json_file_data))
    
    #Comment out N53 vims
    sync_proj_cee_data = get_cee_data_sync_proj(cee_data.json_file_data)
    
    all_vim_data.append(sync_proj_cee_data)
    
    Report_file.add_mesg(Report_file, 'Step 5 ', 'data sync project cee ', str(sync_proj_cee_data))
    
    
    sync_proj_atlas_data = get_atlas_data_sync_proj(atlas_data.json_file_data)
    
    all_vim_data.append(sync_proj_atlas_data)
    
    
    Report_file.add_mesg(Report_file, 'Step 6 ', 'data sync project atlas ', str(sync_proj_atlas_data))
    
    
    log.info('Creating all_vim_templates file for CEE, ATLAS ,ECM , SYNC_PROJ_CEE and SYNC_PROJ_ATLAS ')
    #Comment out N53 vims
    """
    
    final_data = {"vims": all_vim_data}
    
    file_name = 'all_vim_templates.json'

    Json_file_handler.update_json_file(Json_file_handler, file_name, final_data)

    log.info('Created all_vim_templates file for CEE, ATLAS, ECM , SYNC_PROJ_CEE and SYNC_PROJ_ATLAS ')

    Report_file.add_line('Created all_vim_templates file for CEE, ATLAS ,ECM , SYNC_PROJ_CEE and SYNC_PROJ_ATLAS ')


def execute_VNF_LCM_Steps(not_enm,test_hotel=False):
    
    log.info('Start executing VNF_LCM server steps ')
    Report_file.add_line('Start executing VNF_LCM server steps  ')
    
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    
    
    username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    
    if not_enm:
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
    
    else:
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
            
    connection = ServerConnection.get_connection(server_ip, username, password)
    fileExists = ServerConnection.file_exists(server_ip, username, password,
                                               '/vnflcm-ext/current/nfvo/nfvoconfig.json')

    if fileExists:
        log.info('Creating backup of nfvoconfig.json file at path /vnflcm-ext/current/nfvo/ ')
        command = 'sudo -i cp /vnflcm-ext/current/nfvo/nfvoconfig.json /vnflcm-ext/current/nfvo/nfvoconfig.json.orig'
        connection.exec_command(command, get_pty=True)
        Report_file.add_mesg('Step 1 ', 'Created backup of nfvoconfig.json to nfvoconfig.json.orig ',
                             command)
        log.info('Created backup of nfvoconfig.json to nfvoconfig.json.orig ')

    nfvo_data = Initialization_script.get_model_objects(Initialization_script, 'NFVO')
    file_name = 'nfvoconfig.json'
    log.info('updating  nfvoconfig.json file  ')
    execute_json_file_data(nfvo_data.json_file_data, file_name)
    
    if test_hotel:
        log.info('Test Hotel is true, updating the tenant values to the default . ')
        Json_file_handler.update_any_json_attr(Json_file_handler,file_name,[],'userName','ecmadmin')
        Json_file_handler.update_any_json_attr(Json_file_handler,file_name,[],'password','CloudAdmin123')
        Json_file_handler.update_any_json_attr(Json_file_handler,file_name,['tenancyDetails',0],'tenantId','ECM')

    
    if not_enm:        
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'enmHostName', server_ip)    
    
    orvnfm_version = nfvo_data._Nfvo__orvnfm_version
    
    if 'SOL241' == orvnfm_version:
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, [], 'orVnfmVersion', orvnfm_version)
        
    
    sftp = connection.open_sftp()
    log.info('sftp connection opened..')
    # sftp.put(file_name, '/vnflcm-ext/current/nfvo/nfvoconfig.json')
    sftp.put(file_name, '/home/cloud-user/nfvoconfig.json')
    command = 'sudo -i cp /home/cloud-user/nfvoconfig.json /vnflcm-ext/current/nfvo/nfvoconfig.json'
    connection.exec_command(command, get_pty=True)
    log.info('Updated nfvoconfig.json file at path /vnflcm-ext/current/nfvo/ ')
    Report_file.add_mesg('Step 2 ', 'Updated nfvoconfig.json file at path /vnflcm-ext/current/nfvo/  ',
                         str(nfvo_data.json_file_data))

    log.info('Start executing the command to add  nfvoconfig.json file ')
    Report_file.add_line('Start executing the command to add  nfvoconfig.json file ')
    command = 'sudo -i vnflcm nfvo add --file /vnflcm-ext/current/nfvo/nfvoconfig.json'
    stdin, stdout, stderr = connection.exec_command(command, get_pty=True)
    
    command_output = str(stdout.read())
    
    Report_file.add_line('Command Output : ' + command_output)
    
    if 'NFVO addition successful' in command_output:
        
        log.info('NFVO addition is successful ...')
        
    else:
        log.error('Somthing wrong in NFVO addition , please check command output for details' + command_output)    
        assert False


    log.info('Finished executing the command to add  nfvoconfig.json file ')
    Report_file.add_line('Finished executing the command to add  nfvoconfig.json file ')
    
    connection.close()

def vims_addition(not_enm):
    
    log.info('Start executing VNF_LCM vim addition ')
    Report_file.add_line('Start executing VNF_LCM vim addition  ')
    
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    
    
    username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    
    if not_enm:
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
    
    else:
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
            
    connection = ServerConnection.get_connection(server_ip, username, password)
        
    vim_File_Creation(connection)

    file_name = 'all_vim_templates.json'
    log.info('Checking if default vim exists ')
    Report_file.add_line('Checking if default vim exists')

    command = 'sudo -i /usr/local/bin/vnflcm vim list'
    stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

    data = stdout.read()
    string_data = data.decode("utf-8")
    log.info(string_data)

    if 'No data to display' in string_data:

        log.info(' Default Vim does not exists')
        Report_file.add_line(' Default Vim does not exists')

    elif string_data:

        log.info(' Default Vim already added, adding the others vims with all Default as False ')
        Report_file.add_line('Default Vim already added, adding the others vims with all Default as False')
        Json_file_handler.modify_second_level_attr(Json_file_handler, file_name, 'vims', 0, 'defaultVim', 'False')

    log.info('putting all_vim_templates file on server ')
    sftp = connection.open_sftp()
    sftp.put(file_name, '/home/cloud-user/all_vim_templates.json')
    time.sleep(3)
    sftp.close()
    command = 'sudo -i cp /home/cloud-user/all_vim_templates.json /ericsson/vnflcm/data/all_vim_templates.json'
    connection.exec_command(command, get_pty=True)
    log.info('Updated all_vim_templates.json file at path /ericsson/vnflcm/data/ ')
    Report_file.add_mesg('Step 6 ', 'Updated all_vim_templates.json file at path /ericsson/vnflcm/data/  ',
                         '')

    
    log.info('sftp connection closed..')
    command = 'sudo -i vnflcm vim add --file=/ericsson/vnflcm/data/all_vim_templates.json'


    Report_file.add_mesg('Step 7 ', 'Registered VIM ZONE for cee , atlas and ecm_template_vim.json  ',
                         command)

    execute_vims_addition(connection, command)


    log.info('Finished executing VNF_LCM vim addition ')
    Report_file.add_line('Finished executing VNF_LCM vim addition ')

    verify_integration(connection)

    connection.close()


def test_hotel_vim_file(file_name):  
    
    
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    cee_data = Initialization_script.get_model_objects(Initialization_script, 'CEE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    
    name = EPIS_data._EPIS__vimzone_name
    type = EPIS_data._EPIS__cloudManagerType
    host_ip_address = cee_data._Cee__host_ip_address
    hostName = cee_data._Cee__host_name
    authurl = EPIS_data._EPIS__key_stone
    adminUserName = EPIS_data._EPIS__existing_project_admin_username
    adminPassword = EPIS_data._EPIS__existing_project_admin_password
    project_name = EPIS_data._EPIS__existing_project_name
    cee_tenant_id = sit_data._SIT__project_id
    userName = EPIS_data._EPIS__existing_project_user_username
    userPassword = EPIS_data._EPIS__existing_project_user_password

    
    if 'v3' in authurl:
            
            tenants = [{ "userDomain": "Default","name": "Default","id": "default","username": adminUserName,"password": adminPassword,"defaultTenant": "True","subTenants":[{"name": project_name, "id" : cee_tenant_id , "username" : adminUserName ,
                    "password" : adminPassword, "defaultSubTenant" : "True"}]}]
            
    else:
            tenants = [{'name': project_name, 'id' : cee_tenant_id , 'username' : userName ,
                    'password' : userPassword, 'defaultTenant' : "True"}]

    
    data = [{"name": name,"type":type,"defaultVim":"True","hostIpAddress":host_ip_address,"hostName":hostName,"authUrl":authurl,"tenants":tenants}]    
    
    
    Json_file_handler.update_any_json_attr(Json_file_handler,file_name,[],'vims',data)


def test_hotel_vim_addition(not_enm):
    
    log.info('Start executing VNF_LCM vim addition for test hotel ')
    Report_file.add_line('Start executing VNF_LCM vim addition for test hotel')
    
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    
    
    username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
    password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
    
    if not_enm:
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
    
    else:
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
            
    connection = ServerConnection.get_connection(server_ip, username, password)
    
    file_name = 'test_hotel_vim_template.json'
    test_hotel_vim_file(file_name)

    log.info('Checking if default vim exists ')
    Report_file.add_line('Checking if default vim exists')

    command = 'sudo -i /usr/local/bin/vnflcm vim list'
    stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

    data = stdout.read()
    string_data = data.decode("utf-8")
    log.info(string_data)

    if 'No data to display' in string_data:

        log.info(' Default Vim does not exists')
        Report_file.add_line(' Default Vim does not exists')

    elif string_data:

        log.info(' Default Vim already added, adding the others vims with all Default as False ')
        Report_file.add_line('Default Vim already added, adding the others vims with all Default as False')
        Json_file_handler.modify_second_level_attr(Json_file_handler, file_name, 'vims', 0, 'defaultVim', 'False')

    log.info('putting test_hotel_vim_template.json file on server ')
    sftp = connection.open_sftp()
    sftp.put(file_name, '/home/cloud-user/test_hotel_vim_template.json')
    time.sleep(3)
    sftp.close()
    command = 'sudo -i cp /home/cloud-user/test_hotel_vim_template.json /ericsson/vnflcm/data/test_hotel_vim_template.json'
    connection.exec_command(command, get_pty=True)
    log.info('Updated test_hotel_vim_template.json file at path /ericsson/vnflcm/data/ ')
    Report_file.add_line('Updated test_hotel_vim_template.json file at path /ericsson/vnflcm/data/')
    
    log.info('sftp connection closed..')
    command = 'sudo -i vnflcm vim add --file=/ericsson/vnflcm/data/test_hotel_vim_template.json'

    Report_file.add_line('Registered VIM ZONE command ' + command)

    execute_vims_addition(connection, command)


    log.info('Finished executing VNF_LCM vim addition for test hotel ')
    Report_file.add_line('Finished executing VNF_LCM vim addition for test hotel ')

    verify_integration(connection)

    connection.close()
    

if __name__ == "__main__": main()