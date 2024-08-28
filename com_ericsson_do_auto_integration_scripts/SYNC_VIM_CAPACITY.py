
'''
Created on 10 sep 2019

@author: eshetra

'''

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.EPIS_files_update import *
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import ast
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
import random
import time
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities


log = Logger.get_logger('SYNC_VIM_CAPACITY.py')


def create_configuration_file():

    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
    core_hostname = core_vm_hostname.replace('.athtem.eei.ericsson.se','')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    vim_zone_name = EPIS_data._EPIS__sync_vimzone_name

    core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization,'ECMPI')
    username = core_vm_data._Ecm_PI__CORE_VM_USERNAME
    password = core_vm_data._Ecm_PI__CORE_VM_PASSWORD
    deployment_type = core_vm_data._Ecm_PI__deployment_type

    
    if deployment_type == 'HA':
        core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
    else:
        core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
           
    connection = ServerConnection.get_connection(core_vm_ip, username, password)
    
    log.info('start creating hypervisor-default-allocation-ratio.properties file')

    ratio_properties_file = r'com_ericsson_do_auto_integration_files/hypervisor-default-allocation-ratio.properties'
   
    lines = None
    
    with open(ratio_properties_file, 'r') as file_handler:
        
        lines = file_handler.readlines()
        
    
    for line in lines:
        if 'core.ratio.disk = 4' in line:
            index = lines.index(line)
            lines[index] = '''{}.{}.ratio.disk = 4\n'''.format(vim_zone_name,core_hostname)
        elif 'core.ratio.vcpu = 10' in line:
            index = lines.index(line)
            lines[index] = '''{}.{}.ratio.vcpu = 10\n'''.format(vim_zone_name,core_hostname) 
        elif 'core.ratio.memory = 16' in line:
            index = lines.index(line)
            lines[index] = '''{}.{}.ratio.memory = 16\n'''.format(vim_zone_name,core_hostname)
              
        elif 'ratio.disk = 4' in line:
            index = lines.index(line)
            lines[index] = vim_zone_name + '.ratio.disk = 4'+ '\n'
        elif 'ratio.vcpu = 10' in line:
            index = lines.index(line)
            lines[index] = vim_zone_name + '.ratio.vcpu = 10'+ '\n'
        elif 'ratio.memory = 16' in line:
            index = lines.index(line)
            lines[index] = vim_zone_name + '.ratio.memory = 16'+ '\n'       

    
    with open(ratio_properties_file, 'w+') as file_handler:
        
        file_handler.writelines(lines)
        

    file_name1 = r'hypervisor-default-allocation-ratio.properties'      
    sftp = connection.open_sftp()
    sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name1, '/app/ecm/vim-capacity-svc/configuration/' + file_name1)
    sftp.close() 
    log.info('Finished creating and transferring hypervisor-default-allocation-ratio.properties file to core vm on path /app/ecm/vim-capacity-svc/configuration/ ')
    Report_file.add_line(
        'Finished creating and transferring hypervisor-default-allocation-ratio.properties file to core vm on path /app/ecm/vim-capacity-svc/configuration/')
  

    file_name2 = r'configuration.properties'      
    sftp = connection.open_sftp()
    sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name2, '/app/ecm/vim-capacity-svc/configuration/' + file_name2)
    sftp.close()
    log.info('Finished creating and transferring configuration.properties file to core vm on path /app/ecm/vim-capacity-svc/configuration/ ')
    Report_file.add_line('Finished creating and transferring configuration.properties file to core vm on path /app/ecm/vim-capacity-svc/configuration/')

def synch_vim_capacity():
    
    log.info('start executing curl command to sync VIM capacity')
    Report_file.add_line('start executing curl command to sync VIM capacity...')

    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    vim_zone_name = EPIS_data._EPIS__sync_vimzone_name
    
    epis_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization,'ECMPI')
    ecm_server_ip = ecm_host_data._Ecm_PI__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_PI__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_PI__ECM_Host_Blade_Password
    core_vm_ip = ecm_host_data._Ecm_PI__CORE_VM_IP
    #tenant_name = epis_host_data._EPIS__sync_tenant_name

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
       
    curl = '''curl -X POST --insecure  https://{}/ecm_service/vimzones/ecm-vim-capacity-sync-service/synchronize-capacity/{} -H 'Accept: */*'  -H 'Authorization: Basic ZWNtYWRtaW46Q2xvdWRBZG1pbjEyMw==' -H 'Content-Type: application/json' -H 'tenantid: ECM{}'''.format(core_vm_ip,vim_zone_name,"'")

    command = curl
    Report_file.add_line('Sync VIM capacity curl:  ' + command)
    
    command_output = ExecuteCurlCommand.get_json_output(connection, command)

    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)

    requestStatus = output['status']['reqStatus'] 
    if 'SUCCESS' in requestStatus :
        log.info('Sync VIM capacity is successfull ' +command_output)
        Report_file.add_line('Sync VIM capacity is successfull')
    
    elif 'ERROR' in requestStatus :
        
        command_error = output['status']['msgs'][0]['msgText']
        log.error('Error executing curl command for Sync VIM capacity ' +command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for Sync VIM capacity')
        connection.close()
        assert False    
            
    connection.close()    
    log.info('Sync VIM capacity ends')
    Report_file.add_line('Sync VIM capacity ends...')
