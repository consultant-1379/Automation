from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_scripts.EPG_ECM_REDISCOVERY import delete_epg_vapp_entry_cmdb
from com_ericsson_do_auto_integration_scripts.MME_ECM_REDISCOVERY import delete_MME_vapp_entry_cmdb
import time


log = Logger.get_logger('EPG_MME_DISCOVERY.py')

def delete_epg_and_mme_record_from_cmdb():
    try:
        
        log.info('Start to delete EPG record from CMDB')   
        Report_file.add_line('Start to delete EPG record from CMDB')
        delete_epg_vapp_entry_cmdb()
        
        log.info('Start to delete MME record from CMDB')   
        Report_file.add_line('Start to delete MME record from CMDB')
        delete_MME_vapp_entry_cmdb()

    except Exception as e:

        log.error('Failed to delete epg and mme record from cmdb ' + str(e))
        Report_file.add_line('Failed to delete epg and mme record from cmdb' + str(e))
        assert False
        
    
def discovery_of_epg_and_mme():
    try:
        log.info('start to Discover EPG and MME to VDC')
        Report_file.add_line('start to Discover EPG and MME to VDC')
      
        core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization,'ECMPI')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        vnf_type = sit_data._SIT__vnf_type
        
        username = core_vm_data._Ecm_PI__CORE_VM_USERNAME
        password = core_vm_data._Ecm_PI__CORE_VM_PASSWORD
        deployment_type = core_vm_data._Ecm_PI__deployment_type

        if deployment_type == 'HA':
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_IP

        connection = ServerConnection.get_connection(core_vm_ip, username, password)
        
        cd_command = 'cd /app/ecm/vim-discovery-svc'
        
        filename = 'discover-vnfs.py'
        
        vdc_id = EPIS_data._EPIS__vdc_id
       
        
        vnf_manager_id = sit_data._SIT__vnfManagers
        project_name =  EPIS_data._EPIS__project_name
        ecm_gui_username = ecm_host_data._Ecm_core__ecm_gui_username
        ecm_gui_password = ecm_host_data._Ecm_core__ecm_gui_password  
        tenant_name = EPIS_data._EPIS__tenant_name
        nfvo_ip = core_vm_data._Ecm_PI__CORE_VM_IP
        
        command = '''python3 {} --vdcId {} --vnfmId {}   --projectName {} --eocmUser {}   --eocmPwd {}  --tenant {}    --nfvoIp {}'''.format(filename,vdc_id,vnf_manager_id,project_name,ecm_gui_username,ecm_gui_password,tenant_name,nfvo_ip)
        cmd = ''+cd_command+';'+ command
        Report_file.add_line(cmd)
        interact = connection.invoke_shell()
        interact.send(cmd + '\n')
        
        time_out = 120
        wait_time = 5
        ONBOARD_EPG_PACKAGE = sit_data._SIT__epg_vapp_name
        ONBOARD_MME_PACKAGE = sit_data._SIT__mme_package_name
        if vnf_type == 'MME':
            onboard_package_list = [ONBOARD_MME_PACKAGE]
        elif vnf_type == 'EPG':
            onboard_package_list = [ONBOARD_EPG_PACKAGE]
        else:
            onboard_package_list = [ONBOARD_EPG_PACKAGE,ONBOARD_MME_PACKAGE]
        value = len(onboard_package_list)
        count_val = value
        count  = 0
        
        while(time_out !=0):
            resp = interact.recv(9999)
            buff = str(resp)
            
            command_output = buff
            log.info(command_output)
            Report_file.add_line(command_output)
            
            for i in onboard_package_list:
                sucess_msg = 'VNF ['+i+'] was discovered successfully.'
                
                if sucess_msg  in command_output:
                    log.info(sucess_msg)
                    Report_file.add_line(sucess_msg)
                    count = count + 1
                    if count == count_val:
                        return True
                elif 'Deleting file' not in command_output:
                    time_out = time_out - wait_time
                    time.sleep(wait_time) 
                    if time_out == 0:
                        log.info("Waiting time has been exceeded")
                        assert False
                
                else:
                    log.info('Failed to discover VNF Packages')
                    Report_file.add_line('Failed to discover VNF Packages')
                    assert False
        
        
    except Exception as e:

        log.error('Error while discovering the VDC  ' + str(e))
        Report_file.add_line('Error while discovering the VDC' + str(e))
        assert False
        
    finally:
        connection.close()
        
        
