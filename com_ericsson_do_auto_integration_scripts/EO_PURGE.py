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


log = Logger.get_logger('EO_PURGE.py')


def eo_purge():
    #It will delete all the jobs Related to EO
    log.info('Starting EO-PURGE')   
    Report_file.add_line('Starting EO-PURGE')
    purge_file_name= 'purgeDeploymentAndResources.sh'    
    file_name= 'verifyDeploymentDeletion.sh'
 
    
    try:
    
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        helm_deployment_name =sit_data._SIT__helm_deployment_name
        
        ecm_server_ip,ecm_username,ecm_password =  Server_details.ecm_host_blade_details(Server_details)
        environment = Server_details.ecm_host_blade_env(Server_details)
        director_connection = get_VMVNFM_host_connection()

        source_file_path1=r'com_ericsson_do_auto_integration_files/'+purge_file_name
        source_file_path2=r'com_ericsson_do_auto_integration_files/'+file_name
        
        ServerConnection.put_file_sftp(director_connection, source_file_path1, '/home/eccd/' + purge_file_name)
        ServerConnection.put_file_sftp(director_connection, source_file_path2, '/home/eccd/' + file_name)
        
        
        filepath='/home/eccd/'
        
        # Make files executable
        command1 = 'chmod 777 /home/eccd/'+purge_file_name
        command2 = 'chmod 777 /home/eccd/'+file_name
        log.info('giving permission to files '+purge_file_name+' '+file_name)
        stdin, stdout, stderr = director_connection.exec_command(command1)
        stdin, stdout, stderr = director_connection.exec_command(command2)
        
        # Remove Windows line terminators from files
        cmd1 = f'''cd {filepath} ; sed -i 's/\r//' {purge_file_name}'''
        cmd2 = f''' sed -i 's/\r//' {file_name}'''
        log.info('giving permission to '+purge_file_name+' '+file_name)
        stdin, stdout, stderr = director_connection.exec_command(cmd1)
        stdin, stdout, stderr = director_connection.exec_command(cmd2)

        # Check if the Namespace for the intended purge exist
        # if the Namespace does not exist exit
        command_1 = 'kubectl get namespace | grep -i ' + "'"+namespace+"'"
        log.info('Executing command: '+command_1)
        Report_file.add_line('Executing command: ' + command_1)
        stdin, stdout, stderr = director_connection.exec_command(command_1)
        command_output = stdout.read().decode("utf-8")
        log.info('command output :' + command_output)
        Report_file.add_line('command output :' + command_output)
        
        if command_output == "":
            log.info(f'Namespace {namespace} does not exist')
            Report_file.add_line(f'Namespace {namespace} does not exist')
            assert False
        
        # Check if deployment is present, if not carry on
        command_2 = 'helm ls -A | grep -i '+"'"+'eric-eo-'+namespace+"'"
        log.info('Executing command: '+command_2)
        Report_file.add_line('Executing command: ' + command_2)
        stdin, stdout, stderr = director_connection.exec_command(command_2)
        command_output = stdout.read().decode("utf-8")
        log.info('command output :' + command_output)
        Report_file.add_line('command output :' + command_output)
        
        if command_output == '':
            log.info('Deployment is already deleted')
            Report_file.add_line('Deployment is already deleted')
        elif 'eric-eo-'+namespace in command_output:

            # Delete helm deployment
            log.info(f'Deleting deployment {helm_deployment_name}')
            Report_file.add_line(f'Deleting deployment {helm_deployment_name}')
            interact = director_connection.invoke_shell()

            command_3 = f'helm delete {helm_deployment_name} -n {namespace}'
            log.info('Executing command: ' + command_3)
            Report_file.add_line('Executing command: ' + command_3)
            #interact.send(command_3 + '\n')
            #log.info("Waiting for deployment delete to finish")
            #time.sleep(600)
            #resp = interact.recv(9999)
            #buff = resp.decode("utf-8")

            stdin, stdout, stderr = director_connection.exec_command(command_3)
            command_output = stdout.read().decode("utf-8")

            #command_output = buff
            log.info('command output :' + command_output)
            Report_file.add_line('command output :' + command_output)

            if f'release "eric-eo-{namespace}" uninstalled' in command_output:
                log.info(f'release eric-eo-{namespace} uninstalled')
                Report_file.add_line(f'release eric-eo-{namespace} uninstalled')

        #Executing purge script
        log.info(' executing bash script '+purge_file_name)
        Report_file.add_line(' executing bash script ' + purge_file_name)
        command1 = 'cd '+filepath+';./'+purge_file_name+' '+namespace
        log.info(command1)
        Report_file.add_line('command :' + command1)
        stdin, stdout, stderr = director_connection.exec_command(command1)
        command_output = stdout.read().decode("utf-8")
        Report_file.add_line('command output :' + command_output)
        print(command_output)

        #validating resources in the namespace
        command = 'kubectl get pods -n '+namespace
        log.info('Checking the resources by executing command: '+command)
        Report_file.add_line('Checking the resources by executing command: ' + command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = stderr.read()
        Report_file.add_line('command output :' + str(command_output))

        if 'No resources found in '+namespace+' namespace'  in str(command_output):
            log.info('No resources found. '+purge_file_name+' executed successfully')
            Report_file.add_line('No resources found. ' + purge_file_name + ' executed successfully')
            verify_eo_purge(director_connection,file_name,namespace)
        else:
            log.error('Error while executing the file '+purge_file_name + ', check logs for details')
            Report_file.add_line('command output :' + str(command_output))
            assert False

    except Exception as e:
        log.error(str(e))
        Report_file.add_line(str(e))
        assert False

    finally:
        director_connection.close()
        log.info('eccd connection closed.')
        Report_file.add_line('eccd connection closed')


def verify_eo_purge(director_connection, file_name, namespace):
    try:
        filepath = '/home/eccd/'
        log.info('Start Verification to check all the resources are deleted ')
        Report_file.add_line('Start Verification to check all the resources are deleted  ' + file_name)

        command2 = 'cd '+filepath+';./'+file_name+' '+namespace
        log.info(command2)
        Report_file.add_line(' command :' + command2)
        stdin, stdout, stderr = director_connection.exec_command(command2)
        command_output = str(stdout.read())
        Report_file.add_line(' command output :' + command_output)

        output = ast.literal_eval(command_output)
        if 'All PVs for namespace '+namespace+' removed.' in command_output:
            log.info(file_name+' executed successfully')
            Report_file.add_line(file_name + ' executed successfully')
        else:
            log.error('Error while executing the file '+file_name + ', check logs for details')
            assert False

    except Exception as e:
        log.error(str(e))
        Report_file.add_line(str(e))
        assert False
