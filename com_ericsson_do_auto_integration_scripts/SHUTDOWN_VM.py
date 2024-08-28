
import time
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
from com_ericsson_do_auto_integration_scripts.LCM_POST_INSTALLATION import *

log = Logger.get_logger('SHUTDOWN_VM.py')


service_hostname = ''
db_hostname = ''

def fetch_vnflcm_hostname():
    
    try:
        log.info('Fetching the Service and DB hostname')
        Report_file.add_line('Fetching the Service and DB hostname')
        
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        
        check_vnf_lcm_password(server_ip)

        connection = ServerConnection.get_connection(server_ip, username, password)
        global service_hostname
        global db_hostname
        interact = connection.invoke_shell()
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        command = 'sudo -i'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
    
        command = 'hostname'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)    
        buff = str(resp)
        log.info(buff)        
        decode_hostname = resp.decode("utf-8")
        service_hostname = str(decode_hostname).split('\r\n')[1]
        log.info(service_hostname)
        
        command = 'sshdb'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        
        if 'password' in buff:
            interact.send(password+'\n')
            time.sleep(2)
        
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        
        command = 'hostname'
        interact.send(command + '\n')
        time.sleep(2)
        resp = interact.recv(9999)    
        buff = str(resp)
        log.info(buff)        
        decode_hostname = resp.decode("utf-8")
        db_hostname = str(decode_hostname).split('\r\n')[1]
        log.info(db_hostname)             
        
        interact.shutdown(2)

        connection.close()
        log.info('Finished to Fetch the Service and DB hostname')
        Report_file.add_line('Finished to Fetch the Service and DB hostname')

    
    except Exception as e:
        interact.shutdown(2)
        connection.close()
        log.error('Error while Fetching the Service and DB hostname')
        Report_file.add_line('Error while Fetching the Service and DB hostname')
        assert False


def shutdown_vnflcm_vm(project_type):
    
    try:
                
        log.info('Shutting down the Service and DB VM ')
        log.info('waiting 120 seconds for VNF to collect required data from DB')
        time.sleep(120)
        
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        vnf_package_name = sit_data._SIT__name
        
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip =  Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        auth_token = Common_utilities.authToken(Common_utilities,connection,core_vm_hostname)
        
        log.info('Checking the ecm order is created or not ')
        order_status, order_output = Common_utilities.ecm_order_create_status(Common_utilities, connection, auth_token, core_vm_hostname,10,vnf_package_name)
        
        connection.close()
        
        if order_status:
                
            EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')       
                   
            ecm_environment = ecm_host_data._Ecm_core__enviornment
            openstack_ip = EPIS_data._EPIS__openstack_ip
            username = EPIS_data._EPIS__openstack_username
            password = EPIS_data._EPIS__openstack_password
            
            if 'Static' in project_type:            
                
                openrc_filename = 'openrcauto_'+ecm_environment     
                
            else:
                            
                openrc_filename = EPIS_data._EPIS__openrc_filename
                           
            ShellHandler.__init__(ShellHandler,openstack_ip,username,password)
            command = 'source {}'.format(openrc_filename)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
        
            command = 'openstack server stop ' +service_hostname
            Report_file.add_line('Command to shutdown service hostname ' + command)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            time.sleep(5)
        
            command = 'openstack server stop ' +db_hostname
            Report_file.add_line('Command to shutdown db hostname ' + command)
            stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)
            time.sleep(5)
            
            log.info('waiting 30 seconds for completing the shutdown process')
            time.sleep(30)
               
            log.info('Service and DB VM Shutdown')
            Report_file.add_line('Service and DB VM Shutdown')
        
            ShellHandler.__del__(ShellHandler)
        
        else:
            
            log.error('order not created in ECM '+order_output)
            
        
    except Exception as e:
        
        ShellHandler.__del__(ShellHandler)
        log.error('Error in Shutting down the Service and DB VM '+str(e))
        Report_file.add_line('Error in Shutting down the Service and DB VM ' + str(e))
        assert False    
        
