'''
Created on Feb 24, 2021

@author: zaanisn
'''


from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
from bs4 import BeautifulSoup

import json


log = Logger.get_logger('ECDE_SPINNAKER_CLEANUP.py')

def extract_token_for_admin():
 
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
    
    ecde_keycloak_fqdn = ecde_data._Ecde__ecde_keycloak_fqdn
    
    log.info('Login against keycloak as admin')
    
    curl = f'''curl --insecure --request POST 'https://{ecde_keycloak_fqdn}/auth/realms/master/protocol/openid-connect/token'  --header 'Content-Type: application/x-www-form-urlencoded'  --data-urlencode 'grant_type=password' --data-urlencode 'username=admin' --data-urlencode 'password=kcpw' --data-urlencode 'client_id=admin-cli' '''
    command = curl
    Report_file.add_line('login against keycloak as admin using command : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    
    Report_file.add_line('login against keycloak as admin command output : ' + command_output)
 

    output = ast.literal_eval(command_output[2:-1:1])
    
    log.info(output)
    
    if 'access_token' in output:
            
        access_token= output['access_token']
        extract_client_id(connection, ecde_keycloak_fqdn, access_token)
    else:
        log.info('Error while extracting token for admin')
        Report_file.add_line('Error while extracting token for admin')
        assert False

def extract_client_id(connection, ecde_keycloak_fqdn, access_token):
    
    log.info('Extracting all the client configured in the keycloak instance')
    command= f'''curl --insecure --request GET 'https://{ecde_keycloak_fqdn}/auth/admin/realms/eric-cdd/clients/' --header 'Authorization: Bearer {access_token}' '''
    Report_file.add_line('Extracting all the client configured in the keycloak instance using command : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Extracting all the client configured in the keycloak instance command output : ' + command_output)
    output= ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(output)  
        
    if 'error' in output:
        log.info('Error while executing the curl command '+output["error"])
        Report_file.add_line('Error while executing the curl command ' + output["error"])
        assert False
    else:
        for i in output:
            if i["clientId"]=="spinnaker":
                spinnaker_client_id= i['id']
                log.info('Spinnaker Client ID: '+spinnaker_client_id)
                Report_file.add_line('Spinnaker Client ID: ' + spinnaker_client_id)
                extract_secret(connection,ecde_keycloak_fqdn, access_token, spinnaker_client_id)
        
def extract_secret(connection,ecde_keycloak_fqdn, access_token,spinnaker_client_id):
    
    log.info('Extracting the secret associated to client id')
    command= f'''curl --insecure --request GET 'https://{ecde_keycloak_fqdn}/auth/admin/realms/eric-cdd/clients/{spinnaker_client_id}/client-secret' --header 'Authorization: Bearer {access_token}' '''
    Report_file.add_line('Extracting the secret associated to client id using command : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Extracting the secret associated to client id command output : ' + command_output)
    
    output = ast.literal_eval(command_output[2:-1:1])
    
    if "value" in output:
        global client_secret
        client_secret= output["value"]
        log.info('Spinnaker Client Secret: '+client_secret)
        Report_file.add_line('Spinnaker Client Secret: ' + client_secret)
        
    else:
        log.info('Error while executing the curl command : '+output["error"])
        Report_file.add_line('Error while executing the curl command : ' + output["error"])
        assert False
    
def extract_access_token_for_spinnaker():
    
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    ecde_spinnaker_hostname, ecde_spinnaker_user, ecde_spinnaker_password = Server_details.ecde_spinnaker_details(Server_details)
    

    ecde_data = SIT_initialization.get_model_objects(SIT_initialization, 'Ecde')
    
    ecde_keycloak_fqdn = ecde_data._Ecde__ecde_keycloak_fqdn
    
    log.info('Extracting access token for spinnaker')
    command= f'''curl --insecure --request POST 'https://{ecde_keycloak_fqdn}/auth/realms/eric-cdd/protocol/openid-connect/token' --header 'Content-Type: application/x-www-form-urlencoded' --data-urlencode 'grant_type=password' --data-urlencode 'username={ecde_spinnaker_user}' --data-urlencode 'password={ecde_spinnaker_password}' --data-urlencode 'client_id=admin-cli' --data-urlencode 'client_secret={client_secret}' '''
    Report_file.add_line('Extracting access token for spinnaker using command : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('Extracting access token for spinnaker command output : ' + command_output)
    
    output = ast.literal_eval(command_output[2:-1:1])
    
    if 'access_token' in output:
        access_token= output["access_token"]
        pipeline_names= get_all_pipelines(connection, ecde_spinnaker_hostname,access_token)
        if (len(pipeline_names)!=0):
            delete_pipelines(connection,ecde_spinnaker_hostname,access_token,pipeline_names)
        else:
            log.info('No Pipelines to delete , ECDE Spinnaker is already cleaned up')
            Report_file.add_line('No Pipelines to delete , ECDE Spinnaker is already cleaned up')
            
        
    else:
        log.info('Error while executing the curl command : '+output["error"])
        Report_file.add_line('Error while executing the curl command : ' + output["error"])
        assert False
        

def get_all_pipelines(connection,ecde_spinnaker_hostname, access_token):
    
    log.info('Fetching the names of all pipeline')
    command= f'''curl -L --insecure --request GET 'https://{ecde_spinnaker_hostname}/applications/ecde-app/pipelineConfigs' --header 'Authorization: Bearer {access_token}' -b cookie.jar.txt '''
    Report_file.add_line('Curl command : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    Report_file.add_line('command output : ' + command_output)
    command_output= ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_output)
    
    if isinstance(output,list):
        pipeline_names=[]
        for pipeline_details in output:
            pipeline_names.append(pipeline_details["name"])
        
        return(pipeline_names)
    else:
        
        log.info('Error while fetching pipeline names : '+output["error"])
        Report_file.add_line('Error while fetching pipeline names : ' + output["error"])
        assert False
        
            
def delete_pipelines(connection,ecde_spinnaker_hostname,access_token,pipeline_names):
    
    log.info('Starting deletion of pipelines')
    for name in pipeline_names:
        log.info('Deleting pipeline with name '+name)
        command= f'''curl -L --insecure --request DELETE 'https://{ecde_spinnaker_hostname}/pipelines/ecde-app/{name}' --header 'Authorization: Bearer {access_token}' -b cookie.jar.txt '''
        Report_file.add_line('Curl command to delete the pipeline : ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('Deletion curl command output : ' + command_output)
    
        output = (command_output[2:-1:1])
        
        if output=="":
            log.info('Successfully deleted pipeline '+name)
            Report_file.add_line('Successfully deleted pipeline ' + name)
        else:
            soup = BeautifulSoup(output, "html.parser") 
            tag = soup.body 
            for string in tag.strings: 
                error_output=string
                if 'HTTP Status 404' in string:
                    log.info(name+' pipeline not found while deletion: HTTP Status 404')
                    Report_file.add_line(name + ' pipeline not found while deletion: HTTP Status 404')
                    assert False
                elif 'HTTP Status 401' in string:
                    log.info(name+' pipeline deletion failed : Invalid Token')
                    Report_file.add_line(name + ' pipeline deletion failed : Invalid Token')
                    assert False
                else:
                    log.info(name+' pipeline deletion failed due to error : '+error_output)
                    Report_file.add_line(name + ' pipeline deletion failed due to error : ' + error_output)
                    assert False
                    

    