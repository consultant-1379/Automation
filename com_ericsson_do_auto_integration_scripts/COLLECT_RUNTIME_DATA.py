"""
Created on 08 Aug 2020

@author: zsyapra
"""
import json
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from itertools import count

log = Logger.get_logger('COLLECT_RUNTIME_DATA.py')
    
global temp_file,count
temp_file = 'updated_with_new_runtime_data.json'

def update_runtime_data_file(file_path,runtime_data):
    try:
        log.info('Start to update run time file with new updated data' )
        Report_file.add_line('Start to update run time file with new updated data')
        Json_file_handler.update_json_file(Json_file_handler,file_path,runtime_data)
        
    except Exception as e:
        
        log.info('Error while updating the run time file with new data' + str(e))
        Report_file.add_line('Error while updating the run time file with new data' + str(e))
        assert False
        
def compare_runtime_data(runtime_data_from_scripts,runtime_data_from_server):
    log.info("Start to compare the runtime data with server runtime data.")
    Report_file.add_line('Start to compare the runtime data with server runtime data.')
    try:
        count = 0
        filepath = r'com_ericsson_do_auto_integration_files/'+temp_file
        for key, value in runtime_data_from_scripts.items():
            if key not in runtime_data_from_server:
                runtime_data_from_server[key] = value
                log.info('Adding New Key into a file  - ' +key)
                Report_file.add_line('Adding New key ifnot a file - ' + key)
                update_runtime_data_file(filepath,runtime_data_from_server)
                count = count + 1
        
        return count
        
        
    except Exception as e:
        
        log.info('Error while comparing runtime data' + str(e))
        Report_file.add_line('Error while comparing runtime data' + str(e))
        assert False
        
    
def collect_run_time_data():    
    try:
        
        log.info('Start to collect run time data')
        Report_file.add_line('Start to collect run time data')
        
        ecm_server_ip,ecm_username,ecm_password =  Server_details.ecm_host_blade_details(Server_details)
        environment = Server_details.ecm_host_blade_env(Server_details)
        
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        

        runtime_file = 'run_time_' + environment + '.json'
        data_file = 'runtime_data.json'
        data_filepath = r'com_ericsson_do_auto_integration_files/'+data_file
       
        
        command = 'find . -name '+runtime_file
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('Command output - ' + command_output)
        sftp_client = connection.open_sftp()
        
        if runtime_file in command_output:
            with sftp_client.open(runtime_file, 'r') as file_from_server:
                runtime_data_from_server = json.load(file_from_server)
                with open(data_filepath, 'r') as file:
                    runtime_data_from_scripts = json.load(file)
                    count = compare_runtime_data(runtime_data_from_scripts,runtime_data_from_server)
            
            if count == 0:
                log.info("Already Updated to the latest runtime data. ")
                Report_file.add_line('Already Updated to the latest runtime data.')
                assert True
            else:
                Report_file.add_line('Transferring updated file to Server - ' + ecm_server_ip)
                ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + temp_file, runtime_file)
            
        else:
            log.info(runtime_file + "  File does not exit on the server.Hence creating a new runtime file on the server.")
            Report_file.add_line(runtime_file + ' File does not exit on the server.Hence creating a new runtime file on server.')
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + data_file, runtime_file)
            
            
    except Exception as e:
        
        log.info('Error while collecting runtime data' + str(e))
        Report_file.add_line('Error while collecting run time data ' + str(e))
        assert False
    
    finally:
        connection.close()
        
    
