'''
Created on 30 Apr 2020

@author: zsyapra
'''
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_scripts.DUMMY_TOSCA_PRETOSCA_WORKFLOW import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *


log = Logger.get_logger('EOCM_DUMMY_SCALE.py')


def eocm_scaleout():
    try:
        log.info('Start Dummy EOCM ScaleOut ')
        Report_file.add_line('Start Dummy EOCM ScaleOut')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        external_ip_for_services_vm_scale = sit_data._SIT__externalIpForServicesVmToScale
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm
        file_name =  r'VNFD_Wrapper_VNFLAF.json'
        
        update_VNFD_wrapper_SCALE_OUT(file_name)
        if 'TRUE' == is_vm_vnfm:
            
            Common_utilities.transfer_wrapperfile_into_vmvnfm(Common_utilities, file_name)
        
        else:
            
            log.info('making connection with LCM for scale out ')
            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            lcm_conn = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            ServerConnection.put_file_sftp(lcm_conn, r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/' + file_name, r'/home/cloud-user/' + file_name)
            command = 'sudo -i cp /home/cloud-user/'+file_name+ '/vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/'+file_name
            stdin, stdout, stderr = lcm_conn.exec_command(command, get_pty = True)
            time.sleep(2)    
            lcm_conn.close()
        filename = r'scaleOut.json' 
        eocm_dummy_scale_out(filename)
    
    except Exception as e:
        log.error('Error During Dummy EOCM ScaleOut ' + str(e))
        Report_file.add_line('Error During Dummy EOCM Scaleout ' + str(e))
        assert False


def eocm_scalein():
    try:
        log.info('Start Dummy EOCM SCALE-IN ')
        Report_file.add_line('Start Dummy EOCM SCALE-IN')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        external_ip_for_services_vm_scale = sit_data._SIT__externalIpForServicesVmToScale
        is_vm_vnfm = sit_data._SIT__is_vm_vnfm
        
        file_name =  r'VNFD_Wrapper_VNFLAF.json'
        
        update_VNFD_wrapper_SCALE_IN(file_name)
        
        if 'TRUE' == is_vm_vnfm:
            
            Common_utilities.transfer_wrapperfile_into_vmvnfm(Common_utilities, file_name)
            
        else:
            
            log.info('making connection with LCM for scale in')
            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            lcm_conn = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            ServerConnection.put_file_sftp(lcm_conn, r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/' + file_name, r'/home/cloud-user/' + file_name)
            command = 'sudo -i cp /home/cloud-user/'+file_name+ '/vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles/'+file_name
            stdin, stdout, stderr = lcm_conn.exec_command(command, get_pty = True)
            time.sleep(2)    
            lcm_conn.close()
        filename = r'scaleIn.json'
        eocm_dummy_scale_in(filename)
     
    except Exception as e:
        log.error('Error During Dummy EOCM ScaleIn ' + str(e))
        Report_file.add_line('Error During Dummy EOCM Scalein ' + str(e))
        assert False  

def verify_eocm_dummy_scale_workflow_version():
    attribute_name = 'ONBOARD_PACKAGE' 
    node_name = Common_utilities.fetch_attribute_from_runtimefile(Common_utilities,attribute_name)
    verify_worklow_version(node_name)
    
