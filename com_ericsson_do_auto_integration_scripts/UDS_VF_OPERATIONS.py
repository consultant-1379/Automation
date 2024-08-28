
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.UDS_GENERIC_OPERATIONS import UDS_GENERIC as uds_generic
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import ast
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *

log = Logger.get_logger('UDS_VF_OPERATIONS.py')

class UDS_VF:
    def create_vf_in_uds(self,MD5_code,file_name,key_name_to_update):
        try:
            log.info('Start to create the VF')
            Report_file.add_line('Start to create the VF')

            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,connection,uds_hostname,uds_username,uds_password,'master')
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            command = f'''curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Content-MD5: {MD5_code}' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008;HTTP_CSP_FIRSTNAME=Carlos;HTTP_CSP_EMAIL=csantana@sdc.com;HTTP_CSP_LASTNAME=Santana;HTTP_IV_REMOTE_ADDRESS=0.0.0.0;HTTP_CSP_WSTYPE=Intranet;EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources -d @{file_name}'''         
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            

            if "requestError" in command_out or not command_out:
                if "already exists" in command_out:
                    log.info('VF already exists in UDS')
                    Report_file.add_line('VF already exists in UDS')
                    uds_vf_unique_id = Server_details.get_created_vf_id(Server_details)
                    return uds_vf_unique_id
                    
                else:
                    log.error('Request Error While Creating VF, check command output for more details')
                    Report_file.add_line('Request Error While Creating VF , check command output for more details')
                    assert False
            else:
                output = ast.literal_eval(command_out)
                log.info('Fetching out unique id from command out ')
                uds_vf_unique_id = output['uniqueId']
                log.info(f'vf id is {uds_vf_unique_id}')
                Report_file.add_line(f'vf id is {uds_vf_unique_id}')
                update_runtime_env_file(key_name_to_update,uds_vf_unique_id)
                return uds_vf_unique_id


        except Exception as e:
            log.error('Error While creating the VF' + str(e))
            Report_file.add_line('Error While creating the VF' + str(e))
            assert False

        finally:
            connection.close()
            
    def create_vf(self):
        MD5_code  = 'YTMzOGIwYTU1ZDkzOTBhZDM0MjllN2E3YTVlMDYzYmU='
        file_name = 'create_vf.json'
        vf_name = Common_utilities.get_name_with_random_plaintext(Common_utilities,'EpgVF')
        log.info('VF name to would be '+vf_name)
        update_create_VF_file_UDS(file_name, vf_name)
        update_runtime_env_file('UDS_VF_NAME', vf_name)
        key_name_to_update = 'VF_UNIQUE_ID'
        self.uds_vf_unique_id = self.create_vf_in_uds(self,MD5_code,file_name,key_name_to_update)
        

    def add_epg_vfc_to_vf_composition(self):
        file_name = 'add_epg_vfc_to_vf.json'
        vfc_type = 'CERTIFY_EPG'
        epg_certified_vfc_unique_id = Server_details.get_certified_vfc_id(Server_details,vfc_type)
        update_adding_vfc_to_vf_comp_json_files(file_name,epg_certified_vfc_unique_id)
        key_name_to_update = 'UNIQUE_ID_FROM_ADDING_EPG_TO_COMPOSITION'
        self.unique_id_from_adding_epg_to_composition = uds_generic.add_vfc_to_vf_composition(uds_generic,vfc_type,file_name,self.uds_vf_unique_id,key_name_to_update)
        
        
    def add_network_service_vfc_to_vf_composition(self):
        
        file_name = 'add_network_service_vfc_to_vf.json'
        vfc_type = 'CERTIFY_NETWORK_SERVICE'
        ns_certified_vfc_unique_id = Server_details.get_certified_vfc_id(Server_details,vfc_type)  
        update_adding_vfc_to_vf_comp_json_files(file_name,ns_certified_vfc_unique_id)
        key_name_to_update = 'UNIQUE_ID_FROM_ADDING_NS_TO_COMPOSITION'
        self.unique_id_from_adding_ns_composition,self.capabilities_unique_id,self.requirements_unique_id,self.requirements_owner_id = uds_generic.add_vfc_to_vf_composition(uds_generic,vfc_type,file_name,self.uds_vf_unique_id,key_name_to_update)
        
                
    def associate_epg_to_network_service(self):
        try:
            log.info('Start to associate the EPG with the Network Service')
            Report_file.add_line('Start to associate the EPG with the Network Service')
            
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)


            uds_token = Common_utilities.generate_uds_token(Common_utilities,connection,uds_hostname,uds_username,uds_password,'master')

            file_name = 'associate_epg_to_network_service.json'
            vf_unique_id = self.uds_vf_unique_id
            
            update_associate_epg_to_ns_json_file(file_name,self.unique_id_from_adding_epg_to_composition,self.unique_id_from_adding_ns_composition,self.capabilities_unique_id,self.requirements_unique_id,self.requirements_owner_id)

            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            
            command = f'''curl -i --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008;HTTP_CSP_FIRSTNAME=Carlos;HTTP_CSP_EMAIL=csantana@sdc.com;HTTP_CSP_LASTNAME=Santana;HTTP_IV_REMOTE_ADDRESS=0.0.0.0;HTTP_CSP_WSTYPE=Intranet;EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{ vf_unique_id}/resourceInstance/associate -d @{file_name}'''
            
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = command_output[2:-1:1]
            if '200 OK' in command_output:
                log.info('Successfully associated epg to network service')
                Report_file.add_line('Successfully associated epg to network service')
            else:
                log.info('Failed to associate epg to network service')
                Report_file.add_line('Failed to associate epg to network service')
                assert False
            
        except Exception as e:
            log.info('Error while associating epg to network service')
            Report_file.add_line('Error while associating epg to network service')
            assert False
                                 
                                 
   
            
    def onboard_the_ecmrequest_template(self):
        file_name = 'onboard_epg_template.json'
        MD5_code = 'YzU1MGQ5MDQ2NzY3ZjQ1Yzc1YmRiZDNiNmI2MmQ5MDc='
        uds_generic.onboard_the_template(uds_generic,"ecmRequest",file_name,MD5_code,self.uds_vf_unique_id)
           
        
            
    def onboard_the_day1config_template(self):
        file_name = 'onboard_day1_template.json'
        MD5_code = 'MjFmODU5ZTVkZTk4MDQyYjI2MDE4MjI4MWZlNmJhYzg='
        uds_generic.onboard_the_template(uds_generic,"day1Config",file_name,MD5_code,self.uds_vf_unique_id)
           
                
    
    
    def create_epg_inputs(self):
        file_name = 'epg_inputs.json'
       
        epg_vfc_id = Server_details.get_onboarded_vfc_id(Server_details,"EPG")
        nf_vfc_id = Server_details.get_onboarded_vfc_id(Server_details,"NETWORK_FUNCTION")
        update_epg_inputs_json_file(file_name,self.unique_id_from_adding_epg_to_composition,epg_vfc_id,nf_vfc_id)
        uds_generic.create_inputs(uds_generic,file_name,self.uds_vf_unique_id,'EPG')
        
    
            
            
            
    def create_ns_inputs(self):
        file_name = 'network_service_input.json'
        network_service_vfc_id = Server_details.get_onboarded_vfc_id(Server_details,"NETWORK_SERVICE")
        update_ns_input_json_file(file_name,self.unique_id_from_adding_ns_composition,network_service_vfc_id )
        uds_generic.create_inputs(uds_generic,file_name,self.uds_vf_unique_id,'NETWORK_SERVICE')
        
    
    
    def add_epg_properties(self):
        file_name = 'epg_properties.json'
        epg_vfc_id = Server_details.get_onboarded_vfc_id(Server_details,"EPG")
        network_function_vfc_id = Server_details.get_onboarded_vfc_id(Server_details,"NETWORK_FUNCTION")
        update_add_epg_properties_json_file(file_name,epg_vfc_id,network_function_vfc_id)
        uds_generic.add_properties(uds_generic,"EPG",file_name,self.uds_vf_unique_id,self.unique_id_from_adding_epg_to_composition)
    
    def add_ns_properties(self):
        file_name = 'network_service_properties.json'
        resource_vfc_id = Server_details.get_onboarded_vfc_id(Server_details,"RESOURCE")
        network_service_vfc_id = Server_details.get_onboarded_vfc_id(Server_details,"NETWORK_SERVICE")
        update_add_ns_properties_json_file(file_name,resource_vfc_id,network_service_vfc_id)
        uds_generic.add_properties(uds_generic,"NETWORK_SERVICE",file_name,self.uds_vf_unique_id,self.unique_id_from_adding_ns_composition)
        
        
        
    def certify_created_vf(self):
        vf_unique_id = self.uds_vf_unique_id
        uds_generic.certify_uds_vfcs(uds_generic,'CERTIFY_VF',vf_unique_id,'CERTIFY_VF_ID')
