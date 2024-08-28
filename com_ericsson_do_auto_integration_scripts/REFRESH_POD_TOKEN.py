import paramiko
import time
import ast
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization


log = Logger.get_logger('REFRESH_POD_TOKEN.py')

def refresh_pod_token_eo():
    #It will delete all the jobs Related to EO
    log.info('Starting EO POD CLEANUP')
    Report_file.add_line('Starting EO POD CLEANUP')
    refresh_token_file_name= 'refresh_cinder_token.sh'

    try:

        director_connection = get_VMVNFM_host_connection()

        source_file_path1=r'com_ericsson_do_auto_integration_files/'+ refresh_token_file_name

        ServerConnection.put_file_sftp(director_connection, source_file_path1, '/home/eccd/' + refresh_token_file_name)

        
        filepath='/home/eccd/'
        
        #giving file permission
        command1 = 'chmod 777 /home/eccd/'+ refresh_token_file_name
        log.info('giving permission to files '+ refresh_token_file_name)
        stdin, stdout, stderr = director_connection.exec_command(command1)

        #Executing delete pod (refresh_cinder_token.sh) script
        log.info(' executing bash file '+ refresh_token_file_name)
        Report_file.add_line(' executing bash file ' + refresh_token_file_name)
        command1 = 'cd '+filepath+';./'+ refresh_token_file_name
        log.info(command1)
        Report_file.add_line('command :' + command1)
        stdin, stdout, stderr = director_connection.exec_command(command1)
        command_output = str(stdout.read())
        Report_file.add_line('command output :' + command_output)
        output = ast.literal_eval(command_output)

        if 'csi-cinder-controllerplugin deleted.' in command_output:
            log.info(refresh_token_file_name + ' executed successfully')
            Report_file.add_line(refresh_token_file_name + ' executed successfully')
            log.info('************************ ' + command_output)
        elif 'csi-cinder-controllerplugin failed to delete' in command_output:
            log.error(refresh_token_file_name + ' execution failed. csi-cinder-controllerplugin failed to delete')
            Report_file.add_line(refresh_token_file_name + ' execution failed. csi-cinder-controllerplugin failed to delete')
            assert False
        else:
            log.error('Error while executing the file ' + refresh_token_file_name + ', check logs for details')
            assert False
       
    except Exception as e:
        
        log.error(str(e))
        Report_file.add_line(str(e))
        assert False
        
    finally: 
        director_connection.close()
        log.info('eccd connection closed.')
        Report_file.add_line('eccd connection closed')
