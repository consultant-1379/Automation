
# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under which the
# program(s) have been supplied.
#
# ********************************************************************

from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_runtime_env_file
from com_ericsson_do_auto_integration_scripts.UDS_GENERIC_OPERATIONS import UDS_GENERIC as uds_generic
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import ast

log = Logger.get_logger('UDS_SERVICE_OPERATIONS.py')


class UDS_SERVICE:
    
    def create_service(self, file_name, key_name_to_update, MD5_code):
        try:
            log.info('Start to create uds service')
            Report_file.add_line('Start to create uds service')
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            uds_token = Common_utilities.generate_uds_token(Common_utilities,connection,uds_hostname,uds_username,uds_password,'master')

            command = f'''curl --insecure -X POST -H 'Accept: */*' -H 'Content-MD5:{MD5_code}' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; HTTP_CSP_LASTNAME=Santana; HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services -d @{file_name}'''

            Report_file.add_line('create service curl command ' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            if "requestError" in command_out or not command_out:
                
                if "already exists." in command_out:
                    log.info('Service already exists in UDS')
                    Report_file.add_line('Service already exists in UDS')
                    uds_service_id = Server_details.get_uds_service_id(Server_details)
                    return uds_service_id 

                else:
                    log.error('Request Error while creating service, check command output for more details')
                    Report_file.add_line(f'Request Error while creating service, check command output for more details')
                    assert False
            else:
                output = ast.literal_eval(command_out)
                log.info('Fetching out unique id from command out ')
                uds_service_id = output['uniqueId']
                log.info(f'create service id is {uds_service_id}')
                Report_file.add_line(f'create service id is {uds_service_id}')
                update_runtime_env_file(key_name_to_update,uds_service_id )
                return uds_service_id 

        except Exception as e:
            log.error(f'Failed to create UDS Service' + str(e))
            Report_file.add_line(f'Failed to create UDS Service' + str(e))
            assert False

        finally:
            connection.close()


    def create_uds_service(self):
        MD5_code = 'MTcxMmRhNWZjN2EwMWJiMGU4ZmQ4MTQ4ODQ5MmJmYTU='
        file_name = 'create_uds_service.json'
        svc_name = Common_utilities.get_name_with_random_plaintext(Common_utilities, 'EPG_Service')
        log.info('Service name to would be ' + svc_name)
        # using below method also for service because functionality is the same
        # consider changing method's name in the future to more generic
        update_create_VF_file_UDS(file_name, svc_name)
        key_name_to_update = 'UDS_SERVICE_UNIQUE_ID'
        self.uds_service_id = self.create_service(self, file_name, key_name_to_update, MD5_code)


    def add_created_vf_to_the_service(self, file_name, uds_servcie_unique_id):
        try:
            log.info('Start to add create vf to the service')
            Report_file.add_line('Start to add create vf to the service')
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,connection,uds_hostname,uds_username,uds_password,'master')
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            command  = f'''curl -i --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008; HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; HTTP_CSP_LASTNAME=Santana; HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{uds_servcie_unique_id}/resourceInstance -d @{file_name}'''
            Report_file.add_line('certify vfc curl command ' + command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            if '201 Created' in command_output:
                log.info("Successfully added vf to the service  ")  
                Report_file.add_line("Successfully added to the service ")
            else:
                Report_file.add_line('Error while adding service to the vf')
                assert False        
        
        except Exception as e:
            log.error('Error While adding VF to the service ' + str(e))
            Report_file.add_line('Error While adding VF to the service ' + str(e))
            assert False

        finally:
            connection.close()


    def add_vf_to_the_service(self):
        file_name = 'add_vf_to_service.json'
        certify_vf_id = Server_details.get_certified_vfc_id(Server_details,"CERTIFY_VF")
        update_add_vf_to_service_json_file(file_name,certify_vf_id)
        self.add_created_vf_to_the_service(self,file_name,self.uds_service_id)


    def certify_the_service(self):
        self.certified_uds_service_id = uds_generic.certify_uds_vfcs(uds_generic, 'CERTIFIED_SERVICE', self.uds_service_id, 'CERTIFIED_SERVICE_UNIQUE_ID')


    def distribute_the_service_to_so(self, certified_service_unique_id):
        try:
            log.info('Start to distribute the service to SO')
            Report_file.add_line('Start to distribute the service to SO')

            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username, uds_password, 'master')
            
            command = f'''curl -i --insecure  -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Content-Length: 0' -H 'Cookie: JSESSIONID={uds_token};HTTP_IV_USER=cs0008; USER_ID=cs0008; HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; HTTP_CSP_LASTNAME=Santana; HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{certified_service_unique_id}/distribution/PROD/activate'''
                       
            
            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            if '200 OK' in command_output:
                log.info("Successfully distributed the service to the so")  
                Report_file.add_line("Successfully distributed the service to the so")
            else:
                Report_file.add_line('Error while executing the curl command of distribute service to the so')
                assert False        

        except Exception as e:
            log.error('Error while distributing the service to the so ' + str(e))
            Report_file.add_line('Error distributing the service to the so' + str(e))
            assert False

        finally:
            connection.close()


    def distribute_the_service(self):
        self.distribute_the_service_to_so(self,self.certified_uds_service_id)