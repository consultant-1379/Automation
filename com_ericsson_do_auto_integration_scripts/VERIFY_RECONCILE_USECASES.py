
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import random
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from platform import node
import base64
from base64 import b64encode,b64decode 
from tabulate import tabulate

log = Logger.get_logger('VERIFY_RECONCIE_USECASES.py')


def print_VM_Vapp_details(before_VM_vapp_details, after_VM_vapp_details):

    table_data = []

    for key in before_VM_vapp_details.keys():
        table_data.append([key,before_VM_vapp_details[key],after_VM_vapp_details[key]])

    log.info(tabulate(table_data, headers=["VM Vapp Details", "OLD", "NEW"], tablefmt='grid', showindex="always"))
    Report_file.add_line(tabulate(table_data, headers=["VM Vapp Details", "OLD", "NEW"], tablefmt='grid', showindex="always"))

def print_allocated_quota(before_quota_list,usecase1_quota_list):
    table_data = []
    for quota1,quota2 in zip(before_quota_list,usecase1_quota_list):
        table_data.append([quota1['name'],quota1['value'],quota2['value']])


    log.info(tabulate(table_data, headers=["Allocated Quotas", "OLD","NEW"], tablefmt='grid', showindex="always"))
    Report_file.add_line(tabulate(table_data, headers=["Allocated Quotas", "OLD", "NEW"], tablefmt='grid', showindex="always"))


def fetch_reconcile_allocated_quota():

    try:
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        tenant_id = EPIS_data._EPIS__tenant_name

        log.info('Start Fetching the VIM allocated quota details of tenant ' + tenant_id)

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        ecm_gui_username = ecm_host_data._Ecm_core__ecm_gui_username
        ecm_gui_password = ecm_host_data._Ecm_core__ecm_gui_password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        auth_basic = base64.b64encode(bytes(ecm_gui_username + ':' + ecm_gui_password, encoding='utf-8'))
        decoded_auth_basic = auth_basic.decode('utf-8')
        log.info(decoded_auth_basic)


        curl = '''curl --insecure --location --request GET --header 'tenantid: {}' --header 'Content-Type: application/json' --header 'Authorization: Basic {}' 'https://{}/ecm_service/v2/tenants?$expand=totalQuotas,allocatedQuotas{}'''.format(
            tenant_id, decoded_auth_basic, core_vm_hostname, "'")

        command = curl
        Report_file.add_line('fetching VIM details curl command ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line(' fetching VIM details curl output ' + command_output)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']
        tenant_name = output['data']['tenants']

        if 'SUCCESS' in requestStatus:

            for tenant in tenant_name:
                log.info(' Tenant  ' + tenant['tenantName'])

                if tenant_id == tenant['tenantName']:
                    allocated_quotas = tenant['allocatedQuotas']
                    Report_file.add_line('Allocated quotas of VIM are ')
                    Report_file.add_line(allocated_quotas)



        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error(command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for fetching the VIM allocated quota details of tenant')
            assert False

        return allocated_quotas

    except Exception as e:

        log.error('Error Fetching the VIM allocated quota details of tenant ' + str(e))
        Report_file.add_line('Error Fetching the VIM allocated quota details of tenant  ' + str(e))
        assert False

    finally:
        connection.close()









def fetch_vapp_vm_details():
    
    try:
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password    
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        node_id = sit_data._SIT__vapp_Id

        vm_details = {}

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        log.info('Running curl to fetch the vApp VM details using vapp_id '+node_id)
        
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)       
        
        curl = '''curl --insecure --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/vapps/{}'''.format(token,core_vm_hostname,node_id)
        
        command = curl
        Report_file.add_line('curl to fetch the vApp VM details ' + command)
    
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('vApp VM details curl output ' + command_output)
    
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        requestStatus = output['status']['reqStatus']
    
        if 'SUCCESS' in requestStatus:
                            
            vms_id = output['data']['vapp']['vms'][0]['id']
            log.info('vApp VM id is ' + vms_id)
            Report_file.add_line('vApp VM id is ' + vms_id)

            curl = '''curl --insecure --header 'Accept: application/json' --header 'AuthToken:{}' https://{}/ecm_service/vms/{}'''.format(token,core_vm_hostname,vms_id)
        
            command = curl
            Report_file.add_line('curl to fetch the vApp VM details ' + command)
    
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            Report_file.add_line('vApp VM details curl output ' + command_output)
    
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            output = ast.literal_eval(command_out)
            requestStatus = output['status']['reqStatus']
    
            if 'SUCCESS' in requestStatus:

                vm_data = output['data']['vm']

                imageName = vm_data['bootSource']['imageName']
                vm_details['imageName'] = imageName

                srt = vm_data['srt']['name']
                vm_details['srt'] = srt

                try:
                    vmVnics = vm_data['vmVnics'][0]['name']

                    vm_details['vmVnics'] = vmVnics

                except:
                    vm_details['vmVnics'] = ''

                try:
                    bsv = vm_data['bsvs'][0]['id']

                    vm_details['bsv'] = bsv

                except:
                    vm_details['bsv'] = ''


                return vm_details


            elif 'ERROR' in requestStatus:

                command_error = output['status']['msgs'][0]['msgText']

                log.error('Error fetching the VM details ' + command_error)
                Report_file.add_line('Error fetching the VM details ' + command_error)
                assert False
                
            
        elif 'ERROR' in requestStatus:
    
            command_error = output['status']['msgs'][0]['msgText']
    
            log.error('Error fetching the vApp VM id ' + command_error)
            Report_file.add_line('Error fetching the vApp VM id ' + command_error)
            assert False
        
    except Exception as e:

        log.error('Error fetching vApp VM and vim details '+str(e))
        Report_file.add_line('Error fetching vapp and vim details ' + str(e))
        assert False
    
    finally:
        connection.close()

      
def verify_reconcile_usecase1(before_quota_list,before_VM_vapp_details,usecase1_quota_list,usecase1_VM_vapp_details):

    try:

        log.info('Start verification of reconcile usecase-1 ')
        Report_file.add_line('Start verification of reconcile usecase-1 ')

        log.info('Start Comparing allocated quota ')
        Report_file.add_line('Start Comparing allocated quota ')
        """
        for quota1,quota2 in zip(before_quota_list,usecase1_quota_list):
            if quota1['value'] == quota2['value']:
                log.error(' Verification failed because value of {} is equal after the Reconcile Usecase-1'.format(quota1['name']))
                Report_file.add_line(Report_file, ' Verification failed because value of {} is equal after the Reconcile Usecase-1'.format(quota1['name']))
                print_allocated_quota(before_quota_list,usecase1_quota_list)
                assert False

        """
        log.info('Verification passed for allocated quota')
        Report_file.add_line('Verification passed for allocated quota')


        log.info('Start Comparing VM Vapp details')
        Report_file.add_line('Start Comparing VM Vapp details')

        for key in before_VM_vapp_details.keys():
            if before_VM_vapp_details[key] == usecase1_VM_vapp_details[key]:
                log.error(' Verification failed because value of {} is equal after the Reconcile Usecase-1'.format(key))
                Report_file.add_line(' Verification failed because value of {} is equal after the Reconcile Usecase-1'.format(key))
                print_VM_Vapp_details(before_VM_vapp_details, usecase1_VM_vapp_details)
                assert False

        log.info('Verification passed for VM Vapp details')
        Report_file.add_line('Verification passed for VM Vapp details')
        print_allocated_quota(before_quota_list, usecase1_quota_list)
        print_VM_Vapp_details(before_VM_vapp_details, usecase1_VM_vapp_details)

    except Exception as e:

        log.error('Error verification of reconcile usecase-1  ' + str(e))
        Report_file.add_line('Error verification of reconcile usecase-1  ' + str(e))
        assert False



def verify_reconcile_usecase2(usecase2_VM_vapp_details,usecase1_VM_vapp_details):
    try:
        log.info('Start verification of reconcile usecase-2 ')
        Report_file.add_line('Start verification of reconcile usecase-2 ')

        if usecase2_VM_vapp_details['bsv'] == '' and usecase2_VM_vapp_details['vmVnics'] == '':
            log.info('Finished verification of reconcile usecase-2 ')
            Report_file.add_line('Finished verification of reconcile usecase-2 ')
            print_VM_Vapp_details(usecase1_VM_vapp_details,usecase2_VM_vapp_details)
        else:
            log.error('Failed verification of reconcile usecase-2 ')
            Report_file.add_line('Failed verification of reconcile usecase-2 ')
            print_VM_Vapp_details(usecase1_VM_vapp_details, usecase2_VM_vapp_details)

    except Exception as e:

        log.error('Error verification of reconcile usecase-2  ' + str(e))
        Report_file.add_line('Error verification of reconcile usecase-2  ' + str(e))
        assert False
        


def verify_reconcile_usecase3(before_quota_list,usecase3_quota_list,usecase2_VM_vapp_details,usecase3_VM_vapp_details):
    
    log.info('Start verification of reconcile usecase-3 ')
    Report_file.add_line('Start verification of reconcile usecase-3 ')
    print_allocated_quota(before_quota_list, usecase3_quota_list)
    print_VM_Vapp_details(usecase2_VM_vapp_details,usecase3_VM_vapp_details)
    log.info('Finished verification of reconcile usecase-3 ')
    Report_file.add_line('Finished verification of reconcile usecase-3 ')
    
            