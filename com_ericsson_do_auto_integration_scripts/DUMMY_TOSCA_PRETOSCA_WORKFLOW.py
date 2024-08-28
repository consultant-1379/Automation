'''
Created on 16 Sep 2020

@author: zsyapra
'''

from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_initilization import Initialization_script
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DELETION import change_db_passwd_when_permission_denied

log = Logger.get_logger('DUMMY_TOSCA_PRETOSCA_WORKFLOW.py')


def tosca_pretosca_workflow_deployment(path,node_name):
    
    try:
        workflow_deployment(path,node_name)
        second_pkg_path = path+'/package/'
        workflow_deployment(second_pkg_path,node_name)
          
    except Exception as e:
        
        log.info('Error While Installing TOSCA or PRETSOCA workflow '+str(e))
        Report_file.add_line('Error while installing TOSCA or PRETSOCA workflow ' + str(e))
        assert False
        
def install_tosca_pretosca_workflow():
    try:
       
        log.info('Start to install Tosca and PreTosca Work-flow')
        Report_file.add_line('Start to install Tosca and PreTosca Work-flow')
        workflow_pkgs_path = '/var/tmp/Tosca_PreTosca_Workflow'
        node_name = 'TOSCA_PRETOSCA_WORKFLOW'
        tosca_pretosca_workflow_deployment(workflow_pkgs_path,node_name)
        
    except Exception as e:
            log.error('Failed to install Tosca and PreTosca work-flow ' + str(e))
            Report_file.add_line('Failed to install Tosca and PreTosca work-flow ' + str(e))
            assert False  


def modify_workflow_bundle_descriptor():
    try:
        log.info('Start to modify workflow bundle descriptor')
        Report_file.add_line('Start to modify workflow bundle descriptor')
        
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')        
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        
        nested_conn = get_VMVNFM_host_connection()
        
        #Copying file from POD to Local
        pod = get_vmvnfm_pod()
        source_filepath = '/opt/ericsson/ERICvnflafworkflows/useCase-workflow-mapping/vnflaf/2.6.50/vnflaf-2.6.50-WorkflowBundleDescriptor.json'
        dest_filepath = '/home/eccd/vnflaf-2.6.50-WorkflowBundleDescriptor.json'
        get_file_from_vm_vnfm(nested_conn, source_filepath, dest_filepath)
        
        filename = 'vnflaf-2.6.50-WorkflowBundleDescriptor.json'
        filepath = '/home/eccd/'
        key = "supportedPackageTypes"
        new_value = '["HOT"]'
        edit_value_in_file(nested_conn,filepath,key,new_value,filename)
        
        
        #Copying file to POD from Local
        source = ' /home/eccd/vnflaf-2.6.50-WorkflowBundleDescriptor.json'
        destination = '/opt/ericsson/ERICvnflafworkflows/useCase-workflow-mapping/vnflaf/2.6.50/vnflaf-2.6.50-WorkflowBundleDescriptor.json'
        transfer_director_file_to_vm_vnfm(nested_conn,source,destination)
        
        container = 'eric-vnflcm-service'
        change_file_permission_on_pod(nested_conn,pod,container,vm_vnfm_namespace,source_filepath)
        
    except Exception as e:
            log.error('Failed to modify workflow bundle descriptor' + str(e))
            Report_file.add_line('Failed to modify workflow bundle descriptor' + str(e))
            assert False
    finally:
        nested_conn.close()
        

def fetch_external_management_id(node_name):
    try:
        log.info('Start to fetch External Management ID from EOCM')
        Report_file.add_line('Start to fetch External Management ID from EOCM')
        ecm_server_ip,ecm_username,ecm_password =  Server_details.ecm_host_blade_details(Server_details)
        #core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        #core_vm_ip,core_vm_username,core_vm_password =  Server_details.core_vm_details(Server_details, 'core_vm_ip')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        
        vapp_list = get_vapp_list_from_eocm(connection,token,core_vm_hostname,"ALL")
        for vapp_dict in vapp_list:
            vapp_name = vapp_dict['name']
           
            if vapp_name == node_name:
                my_key = 'managementSystemId'
                managementsystemId = id = vapp_dict['managementSystemId']
                Report_file.add_line('External Management ID - ' + managementsystemId)
                return managementsystemId
                
                    
                        
    except Exception as e:
            log.error('Failed to Fetch External Management Id From EOCM ' + str(e))
            Report_file.add_line('Failed to Fetch External Management Id From EOCM ' + str(e))
            assert False  
    finally:
        connection.close()
        
        
def compare_and_verify_workflowbundleversion(output):
    try:
        res = output.split('\n')
        for x in res:
            row = x.split('|')
            for index, value in enumerate(row): 
                if index == 2:
                    value = value.strip()
                    if value == 'workflowbundleversion' :
                        pass
                    else:
                        if value == '2.6.48-SNAPSHOT' or value == '2.6.50' :
                           
                            log.info('Successfully Verified workflow bundle verison for '+row[3]+'.Installed veriosn is '+value+'')
                            Report_file.add_line('Successfully Verified workflow bundle verison for ' + row[3] + '.Installed veriosn is ' + value + '')
                            
                        else:
                            log.info('Failed to verify Work-flow bundle version for '+row[3]+'\nInstalled Version - '+row[2]+'\nvnflifecycleoperationid - '+row[0])
                            Report_file.add_line(
                                'Failed to verify Work-flow bundle version for ' + row[3] + '\nInstalled Version - ' + row[2] + '\nvnflifecycleoperationid - ' + row[0])
                            assert False
                            
    except Exception as e:
            log.error('Failed to Fetch External Management Id From EOCM ' + str(e))
            Report_file.add_line('Failed to Fetch External Management Id From EOCM ' + str(e))
            assert False
            

def verify_workflow_version_on_vm_vnfm(node_name):
    try:
        log.info('Start to verify Tosca and PreTosca Workflow verison on VM VNFM')
        Report_file.add_line('Start to verify Tosca and PreTosca Workflow verison on VM VNFM')
        
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')        
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        nested_conn = get_VMVNFM_host_connection()
        
        filename = 'vnflifecycleOperationData.sh'
        source_filepath = r'com_ericsson_do_auto_integration_files/'+filename
        dest_filepath = f'/tmp/{filename}'
        ServerConnection.put_file_sftp(nested_conn, source_filepath, dest_filepath)
        
        pod = get_vmvnfm_pod()
        destination = f'/tmp/{filename}'
        #Converting Windows format to Unix format
        cmd = f'''sed -i 's/\r//' {destination}'''
        Report_file.add_line('Command - ' + cmd)
        stdin, stdout, stderr = nested_conn.exec_command(cmd)
        command_output = str(stdout.read())
        
        transfer_director_file_to_vm_vnfm(nested_conn,dest_filepath,destination)
        source_filepath = '/'+filename
        
        container = 'eric-vnflcm-service'
        change_file_permission_on_pod(nested_conn,pod,container,vm_vnfm_namespace,source_filepath)
        
        vnfInstanceId = fetch_external_management_id(node_name)

        cmd = f".{destination} '{vnfInstanceId}' '{node_name}' "
        
        command = get_vmvnfm_pod_cmd(cmd)
        Report_file.add_line('command  : ' + command)
        stdin, stdout, stderr = nested_conn.exec_command(command)     
        command_output = str(stdout.read())
        output = ast.literal_eval(command_output[1:])
        Report_file.add_line('command Output : ' + output)
        if '(0 rows)' in output:
                log.info('Please do check if workflow is installed for TOSCA or PRE-TOSCA.Please do check if Dummy TOSCA or PRE-TOSCA is deployed or not')
                Report_file.add_line('Please do check if workflow is installed for TOSAC or PRE-TOSCA.Please do check if Dummy TOSCA or PRE-TOSCA is deployed or not')
                assert False
        compare_and_verify_workflowbundleversion(output)
        
                        
            
        
    except Exception as e:
            log.error('Error While verifying workflow verison ' + str(e))
            Report_file.add_line('Error While verifying workflow verison ' + str(e))
            assert False  
    finally:
        nested_conn.close()
        
        
def verify_workflow_verison_on_lcm(node_name):
    try:
        log.info('Start to verify Tosca and PreTosca Workflow verison on LCM')
        Report_file.add_line('Start to verify Tosca and PreTosca Workflow verison on LCM')
       
        vnfInstanceId = fetch_external_management_id(node_name)
        db_query = '''select vnflifecycleoperationid,vnfid,workflowbundleversion,businesskey from vnflifecycleoperation where  vnfid ='{}' and businesskey  LIKE '%{}%'; '''.format(vnfInstanceId,node_name)
       
        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
        log.info('Connecting to LCM Server '+lcm_server_ip)
        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
            
        interact = connection.invoke_shell()
        time.sleep(2)
        
        command = 'sudo -i'
        interact.send(command + '\n')
        time.sleep(2)
        
        command = 'sshdb'
        interact.send(command + '\n')
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if "vnflaf-db's password" in buff:
            interact.send(lcm_password + '\n')
            time.sleep(4)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'Permission denied' in buff:
                # same has to update in multiple places when pushing the code
                log.info('Permission denied , password has been changed . Going to set it again')
                change_db_passwd_when_permission_denied(interact, lcm_password)

        command = '''sudo -u postgres psql -d vnflafdb '''
        interact.send(command + '\n')
        time.sleep(4)
        
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        #buff = buff.decode(encoding='UTF-8')
        log.info('Converted to string '+buff+'')
        if 'vnflafdb=' in buff:
            command = db_query
            Report_file.add_line('Command -' + command)
            interact.send(command + '\n')
            time.sleep(4)
            
            resp = interact.recv(9999).decode()
            Report_file.add_line('Command Output -' + resp)
            out = resp.split(';')[1]
            if '(0 rows)' in out:
                log.info('Please do check if workflow is installed for TOSCA or PRE-TOSCA.Please do check if Dummy TOSCA or PRE-TOSCA is deployed or not')
                Report_file.add_line('Please do check if workflow is installed for TOSAC or PRE-TOSCA.Please do check if Dummy TOSCA or PRE-TOSCA is deployed or not')
                assert False
            output = out.split('\r\n----------------\r\n')
            log.info(output)
            for index, value in enumerate(output):
                if index == 1:
                    result = value.split(node_name)
                    for i in result:
                        if 'rows)' in i:
                            return
                        val = i.split('|')[2]
                        val1 = val.replace('\r\n', '')
                        insatlled_version = val1.strip()
                        if insatlled_version == '2.6.48-SNAPSHOT' or insatlled_version == '2.6.50' :
                           
                            log.info('Successfully Verified installed Work-flow bundle version. Installed version '+insatlled_version+' for '+node_name)
                            Report_file.add_line('Successfully Verified installed Work-flow bundle version. Installed version ' + insatlled_version + ' for ' + node_name)
                            
                        else:
                            vnflifecycleoperationid = i.split('|')[0]
                            vnfid = i.split('|')[1]
                            businesskey   = i.split('|')[3]
                            log.info('Failed to verify Work-flow bundle version for '+businesskey+'\nInstalled Version - '+insatlled_version+'\nvnflifecycleoperationid - '+vnflifecycleoperationid+'\nvnfid - '+vnfid+'')
                            Report_file.add_line(
                                'Failed to verify Work-flow bundle version for ' + businesskey + '\nInstalled Version - ' + insatlled_version + '\nvnflifecycleoperationid - ' + vnflifecycleoperationid + '\nvnfid - ' + vnfid + '')
                            assert False
        else:
            log.info('Could not find vnflafdb in the output')
            Report_file.add_line('Could not find vnflafdb in the output')
            assert False
        interact.shutdown(2)
            
        

    except Exception as e:
        log.error('Error While Verifying Workflow bundle version' + str(e))
        Report_file.add_line('Error verifying Workflow bundle version ' + str(e))
        assert False
    finally:
        connection.close()


def verify_worklow_version(node_name):
    try:
        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

        if 'TRUE' == is_vm_vnfm:
            verify_workflow_version_on_vm_vnfm(node_name)
        else:
            verify_workflow_verison_on_lcm(node_name)
    except Exception as e:
        assert False
                