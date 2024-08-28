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
import ast
import json
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import *
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import *


log = Logger.get_logger('UDS_VNF_PRE_REQ.py')

class UDS_VNF_PRE_REQ:
    
    def create_vlm(self):
        try:
            log.info('Starting to Create VLM..')
            Report_file.add_line('Starting to Create VLM..')
            file_name="createVLM.json"
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection_ecm = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,connection_ecm,uds_hostname,uds_username,uds_password,'master')
            global vendorName
            
            vendorName= Common_utilities.get_name_with_timestamp(Common_utilities,'Ericsson')
            vendorName=vendorName.replace('_','')
            vendorName=vendorName.replace('-','')

            update_create_vlm_json_file(file_name, vendorName)

            ServerConnection.put_file_sftp(connection_ecm, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            
            command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @createVLM.json https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-license-models'''         
            command_output = ExecuteCurlCommand.get_json_output(connection_ecm, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            command_out= ast.literal_eval(command_out)
            log.info(command_out)
            if "itemId" and "version" in command_out:
                global vlm_item_id
                for i in command_out:
                    item_id = command_out["itemId"]
                    version_id = command_out["version"]["id"]
                    vlm_item_id= item_id
                log.info('Item ID: '+str(item_id))
                Report_file.add_line('Item Id: ' + str(item_id))
                log.info('Version ID: '+str(version_id))
                Report_file.add_line('Version Id: ' + str(version_id))
                
                log.info('VLM Created.')
                Report_file.add_line('VLM Created.')
                self.submit_vlm(self,connection_ecm,uds_token,item_id,version_id)
            else:
                log.error('Some error encountered While creating the VLM ' + str(command_out))
                Report_file.add_line('Some error encountered While creating the VLM ' + str(command_out))
                connection_ecm.close()
                assert False      
        except Exception as e:
            log.error('Error While creating the VLM ' + str(e))
            Report_file.add_line('Error While creating the VLM ' + str(e))
            connection_ecm.close()
            assert False
        
    def submit_vlm(self,connection_ecm,uds_token,item_id,version_id):
        try:
            log.info('Starting to submit the  VLM..')
            Report_file.add_line('Starting to submit the VLM..')
            file_name= "submit.json"
            ServerConnection.put_file_sftp(connection_ecm, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            command = f'''curl --insecure -X PUT -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @submit.json https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-license-models/{item_id}/versions/{version_id}/actions'''         
            command_output = ExecuteCurlCommand.get_json_output(connection_ecm, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            log.info(command_out)
            if  command_out=='{}':
                log.info(f'Successfully submitted the VLM.')
                Report_file.add_line(f'Successfully submitted the VLM.')
            else:
                log.info(f'Failed to submit the VLM.')
                Report_file.add_line(f'Failed to submit the VLM.')
                assert False      
        except Exception as e:
            log.error('Error While creating the VLM ' + str(e))
            Report_file.add_line('Error While creating the VLM ' + str(e))
            assert False
        finally:
            connection_ecm.close()
               
    def create_vsp(self):
        try:
            log.info('Starting to Create VSP..')
            Report_file.add_line('Starting to Create VSP..')
            file_name="createVSP.json"
            file_path= r'com_ericsson_do_auto_integration_files/UDS_files/'+file_name
            global vspName
            vspName= Common_utilities.get_name_with_timestamp(Common_utilities,'ETSI_TOSCA_VSP')
            vspName=vspName.replace('_','')
            vsprName=vspName.replace('-','')

            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            blade_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,blade_connection,uds_hostname,uds_username,uds_password,'master')
            update_create_vsp_json_file(file_name,vendorName, vspName,vlm_item_id)

            ServerConnection.put_file_sftp(blade_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @createVSP.json https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products'''         
            command_output = ExecuteCurlCommand.get_json_output(blade_connection,
                                                                command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            command_out= ast.literal_eval(command_out)
            log.info(command_out)

            global item_id 
            global version_id
            if "itemId" and "version" in command_out:
                for i in command_out:
                    item_id = command_out["itemId"]
                    version_id = command_out["version"]["id"]
                log.info('Item ID: '+str(item_id))
                Report_file.add_line('Item Id: ' + str(item_id))
                log.info('Version ID: '+str(version_id))
                Report_file.add_line('Version Id: ' + str(version_id))
                
                log.info('VSP Created.')
                Report_file.add_line('VSP Created.')
                self.attach_package(self,uds_token,blade_connection)

            else:
                log.error('Some error encountered While creating the VSP ' + str(command_out))
                Report_file.add_line('Some error encountered While creating the VSP ' + str(command_out))
                blade_connection.close()
                assert False      
        except Exception as e:
            log.error('Error While creating the VSP ' + str(e))
            Report_file.add_line('Error While creating the VSP ' + str(e))
            blade_connection.close()
            assert False
    
    def attach_package(self,uds_token,blade_connection):
        try:
            log.info('Starting to attach the package..')
            Report_file.add_line('Starting to attach the package..')
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
            software_path = sit_data._SIT__epgToscaSoftwarePath
            file_name= software_path+'/'+'Tosca_EPG_VNFD.csar'
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            command= f'''curl --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: multipart/form-data' -H 'Accept: application/json' -H 'USER_ID: cs0008' -F 'upload=@"{file_name}"' https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/versions/{version_id}/orchestration-template-candidate'''            
            log.info(command)
            
            command_output = ExecuteCurlCommand.get_json_output(blade_connection,
                                                                command)
            log.info(command_output)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            command_out= ast.literal_eval(command_out)
            log.info(command_out)

            if command_out["status"]=="Success":
                log.info(f'Successfully attached the package.')
                Report_file.add_line(f'Successfully attached the package.')
            else:
                log.info(f'Failed to attached the package: '+str(command_out["error"]))
                Report_file.add_line(f'Failed to attached the package: ' + str(command_out["error"]))
                blade_connection.close()
                assert False    
        except Exception as e:
            log.error('Error While attaching package ' + str(e))
            Report_file.add_line('Error While attaching package ' + str(e))
            blade_connection.close()
            assert False
        finally:
            blade_connection.close()
        
    def process_vsp(self):
        try:
            log.info('Starting to process VSP..')
            Report_file.add_line('Starting to process VSP..')
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            ecm_blade_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            file_name="test.json"
            uds_token = Common_utilities.generate_uds_token(Common_utilities,ecm_blade_connection,uds_hostname,uds_username,uds_password,'master')
            ServerConnection.put_file_sftp(ecm_blade_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            command = f'''curl --insecure -X PUT -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' --data @test.json https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/versions/{version_id}/orchestration-template-candidate/process'''         
            command_output = ExecuteCurlCommand.get_json_output(ecm_blade_connection,
                                                                command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            command_out= ast.literal_eval(command_out)
            log.info(command_out)

            if command_out["status"]=="Success":
                log.info(f'Successfully processed VSP.')
                Report_file.add_line(f'Successfully processed VSP.')
            else:
                log.info(f'Failed to process VSP: '+str(command_out["error"]))
                Report_file.add_line(f'Failed to process VSP: ' + str(command_out["error"]))
                assert False      
        except Exception as e:
            log.error('Error While process VSP ' + str(e))
            Report_file.add_line('Error While process VSP ' + str(e))
            ecm_blade_connection.close()
            assert False
        finally:
            ecm_blade_connection.close()
        
    def commit_vsp(self):
        try:
            log.info('Starting to commit the VSP..')
            Report_file.add_line('Starting to commit the VSP..')
            file_name="commitVSP.json"
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            blade_server_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,blade_server_connection,uds_hostname,uds_username,uds_password,'master')
            ServerConnection.put_file_sftp(blade_server_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            command = f'''curl -i --insecure -X PUT -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @commitVSP.json https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/items/{item_id}/versions/{version_id}/actions'''         
            command_output = ExecuteCurlCommand.get_json_output(blade_server_connection,
                                                                command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            log.info(command_out)

            if '200 OK' in command_output or command_out=='':
                log.info(f'Successfully committed the VSP.')
                Report_file.add_line(f'Successfully committed the VSP.')
                self.submit_vsp(self,blade_server_connection,uds_token)
            else:
                log.info(f'Failed to commit the VSP.')
                Report_file.add_line(f'Failed to commit the VSP.')
                blade_server_connection.close()
                assert False      
        except Exception as e:
            log.error('Error While commiting the VSP ' + str(e))
            Report_file.add_line('Error While committing the VSP ' + str(e))
            blade_server_connection.close()
            assert False
            
    def submit_vsp(self,blade_server_connection,uds_token):
        try:
            log.info('Starting to submit the VSP..')
            Report_file.add_line('Starting to submit the VSP..')
            file_name="submit.json"
            ServerConnection.put_file_sftp(blade_server_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            command = f'''curl -i --insecure -X PUT -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @submit.json https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/versions/{version_id}/actions'''         
            command_output = ExecuteCurlCommand.get_json_output(blade_server_connection,
                                                                command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            log.info(command_out)
           
            if '200 OK' in command_output or command_out=='':
                log.info(f'Successfully submitted the VSP.')
                Report_file.add_line(f'Successfully submitted the VSP.')
            else:
                log.info(f'Failed to submit the VSP.')
                Report_file.add_line(f'Failed to submit the VSP.')
                assert False      
        except Exception as e:
            log.error('Error While submitting the VSP ' + str(e))
            Report_file.add_line('Error While submitting the VSP ' + str(e))
            assert False
        finally:
            blade_server_connection.close()
        
    def create_vsp_package(self):
        try:
            log.info('Starting to create VSP package..')
            Report_file.add_line('Starting to create VSP package..')
            file_name="createPackage.json"
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            new_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,new_connection,uds_hostname,uds_username,uds_password,'master')
            ServerConnection.put_file_sftp(new_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            
            command = f'''curl --insecure -X PUT -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @createPackage.json https://{uds_hostname}/sdc1/feProxy/onboarding-api/v1.0/vendor-software-products/{item_id}/versions/{version_id}/actions'''         
            command_output = ExecuteCurlCommand.get_json_output(new_connection, command)
            log.info(command_output)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            log.info(command_out)
           
            if 'vspName' in command_output:
                log.info(f'Successfully created VSP package.')
                Report_file.add_line(f'Successfully created VSP package.')
                self.import_vsp_as_vf(self,new_connection,uds_token)
            else:
                log.info(f'Failed to create VSP package.')
                Report_file.add_line(f'Failed to create VSP package.')
                new_connection.close()
                assert False    
        except Exception as e:
            log.error('Error While creating VSP package ' + str(e))
            Report_file.add_line('Error While creating VSP package ' + str(e))
            new_connection.close()
            assert False
            
    def import_vsp_as_vf(self,new_connection,uds_token):
        try:
            log.info('Starting to import VSP as VF..')
            Report_file.add_line('Starting to import VSP as VF..')
            vsp_name_value = vspName.replace('-','').lower()
            #log.info(vsp_name_value)
            file_name= "importVSPasVF.json"
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            update_import_vsp_as_vf_json_file(file_name,item_id,version_id,vendorName,vspName)
            MD5_code = Common_utilities.generate_MD5_checksum_for_json(Common_utilities, r'com_ericsson_do_auto_integration_files/UDS_files/'+file_name)

            ServerConnection.put_file_sftp(new_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            
            command = f'''curl --insecure -X POST 'https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/' -H 'Accept: application/json, text/plain, */*' -H 'Cache-Control: no-cache' -H 'Connection: keep-alive' -H 'Content-MD5: {MD5_code}' -H 'Content-Type: application/json;charset=UTF-8' -H 'Cookie: USER_ID=cs0008;JSESSIONID={uds_token}' -d @importVSPasVF.json > importvspasVF_result.json'''            
            command_output= ExecuteCurlCommand.get_json_output(new_connection, command)
            source= '/root/importvspasVF_result.json'
            destination= r'com_ericsson_do_auto_integration_files/UDS_files/importvspasVF_result.json'
            ServerConnection.get_file_sftp(new_connection, source, destination)
           
            command_out=command_output[2:-1:1]
            
            value='vsp'+str(vsp_name_value)+'informationtxt'

            f = open(r'com_ericsson_do_auto_integration_files/UDS_files/importvspasVF_result.json','r')
            data = json.loads(f.read())
            log.info(data)
            if 'artifacts' in data:
                id= data['artifacts'][value]['uniqueId']
                id=id.split('.')[0]
                log.info('VSP as VF unique ID: '+str(id))
                self.certify_vf(self,new_connection,uds_token,id)
            else:
                log.info(f'Failed to import VSP as VF.')
                Report_file.add_line(f'Failed to import VSP as VF.')
                new_connection.close()
                assert False
             
        except Exception as e:
            log.error('Error While importing VSP as VF ' + str(e))
            Report_file.add_line('Error While importing VSP as VF ' + str(e))
            new_connection.close()
            assert False
            
    def certify_vf(self,new_connection,uds_token,vsp_as_vf_unique_id):
        try:
            log.info('Starting to certify the VF..')
            Report_file.add_line('Starting to certify the VF..')
            file_name="certifyVF.json"
            ServerConnection.put_file_sftp(new_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

            global certify_vf_unique_id
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @certifyVF.json https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{vsp_as_vf_unique_id}/lifecycleState/certify'''         
            command_output = ExecuteCurlCommand.get_json_output(new_connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            command_out= ast.literal_eval(command_out)
            log.info(command_out)

            if 'uniqueId' in command_output:
                certify_vf_unique_id = command_out["uniqueId"]
                certify_vf_unique_id=certify_vf_unique_id.split('.')[0]
        
                log.info(certify_vf_unique_id)
                Report_file.add_line(f'Unique Id: ' + str(certify_vf_unique_id))
                log.info(f'Successfully certified the VF.')
                Report_file.add_line(f'Successfully certified the VF.')
            else:
                log.info(f'Failed to certify the VF.')
                Report_file.add_line(f'Failed to certify the VF.')
                assert False      
        except Exception as e:
            log.error('Error While certifying the VF ' + str(e))
            Report_file.add_line('Error While certifying the VF ' + str(e))
            assert False
        finally:
            new_connection.close()
    def create_vnf_service(self):
        try:
            log.info('Starting to create VNF service..')
            Report_file.add_line('Starting to create VNF service..')
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,ecm_connection,uds_hostname,uds_username,uds_password,'master')
            file_name="createVNFService.json"
            update_create_vnf_service_json_file(file_name,vspName)

            ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @createVNFService.json https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services'''         
            command_output = ExecuteCurlCommand.get_json_output(ecm_connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            command_out= ast.literal_eval(command_out)
            log.info(command_out)

            if 'properties' in command_output:
                vnf_service_unique_id = command_out["properties"][0]["uniqueId"]
                vnf_service_unique_id =vnf_service_unique_id.split('.')[0]
                log.info(vnf_service_unique_id)
                Report_file.add_line(f'Unique Id: ' + str(vnf_service_unique_id))
                log.info(f'Successfully created VNF service.')
                Report_file.add_line(f'Successfully created VNF service.')
                self.add_vf_to_vnf_service(self,uds_token,ecm_connection,vnf_service_unique_id)
            else:
                log.info(f'Failed to create VNF service.')
                Report_file.add_line(f'Failed to create VNF service.')
                ecm_connection.close()
                assert False      
        except Exception as e:
            log.error('Error While creating VNF service ' + str(e))
            Report_file.add_line('Error While creating VNF service ' + str(e))
            ecm_connection.close()
            assert False
            
    def add_vf_to_vnf_service(self,uds_token,ecm_connection,vnf_service_unique_id):
        try:
            log.info('Starting to add vf to vnf service..')
            Report_file.add_line('Starting to add vf to vnf service..')
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            file_name= "addVFtoVNFService.json"
            update_add_vf_to_vnf_service_json_file(file_name,certify_vf_unique_id)
            ServerConnection.put_file_sftp(ecm_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            command = f'''curl -i --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @addVFtoVNFService.json https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{vnf_service_unique_id}/resourceInstance'''         
            command_output = ExecuteCurlCommand.get_json_output(ecm_connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            
            if '201 Created' in command_output:
                log.info(f'Successfully added vf to vnf service.')
                Report_file.add_line(f'Successfully added vf to vnf service.')
                self.certify_service(self,vnf_service_unique_id)
            else:
                log.info(f'Failed to add vf to vnf service.')
                Report_file.add_line(f'Failed to add vf to vnf service.')
                ecm_connection.close()
                assert False      
        except Exception as e:
            log.error('Error While adding vf to vnf service ' + str(e))
            Report_file.add_line('Error While adding vf to vnf service ' + str(e))
            ecm_connection.close()
            assert False
        
            
    def certify_service(self,vnf_service_unique_id):
        try:
            log.info('Starting to certify service..')
            Report_file.add_line('Starting to certify service..')
            
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            new_ecm_server_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,new_ecm_server_connection,uds_hostname,uds_username,uds_password,'master')
            file_name="certify.json"
            ServerConnection.put_file_sftp(new_ecm_server_connection, r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                           SIT.get_base_folder(SIT) + file_name)

            command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' -d @certify.json https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{vnf_service_unique_id}/lifecycleState/certify > output_CertifyService.json'''         
            command_output = ExecuteCurlCommand.get_json_output(
                new_ecm_server_connection, command)
            source= '/root/output_CertifyService.json'
            destination= r'com_ericsson_do_auto_integration_files/UDS_files/output_CertifyService.json'
            ServerConnection.get_file_sftp(new_ecm_server_connection, source, destination)
            f = open(r'com_ericsson_do_auto_integration_files/UDS_files/output_CertifyService.json','r')
            data = json.loads(f.read())
            log.info(data)
            certify_service_unique_id=''
            if 'uniqueId' in data:
                certify_service_unique_id = data["uniqueId"]
                certify_service_unique_id=certify_service_unique_id.split('.')[0]
                log.info(certify_service_unique_id)
                Report_file.add_line(f'Unique Id: ' + str(certify_service_unique_id))
                log.info(f'Successfully certified service.')
                Report_file.add_line(f'Successfully certified service.')
                #self.onboarding_so_subsytems(self)
                self.distribute_service(self,certify_service_unique_id)
            else:
                log.info(f'Failed to certify service.')
                Report_file.add_line(f'Failed to certify service.')
                new_ecm_server_connection.close()
                assert False      
        except Exception as e:
            log.error('Error While certifying service ' + str(e))
            Report_file.add_line('Error While certifying service ' + str(e))
            new_ecm_server_connection.close()
            assert False
        finally:
            new_ecm_server_connection.close()
    
    def onboarding_so_subsytems(self):
    
        onboard_enm_ecm_subsystems('subsystem')
        
    def distribute_service(self,certify_service_unique_id):
        try:
            log.info('Starting to distribute service..')
            Report_file.add_line('Starting to distribute service..')
            uds_hostname,uds_username,uds_password = Server_details.get_uds_host_data(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection_with_ecm = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            uds_token = Common_utilities.generate_uds_token(Common_utilities,connection_with_ecm,uds_hostname,uds_username,uds_password,'master')
            
            command = f'''curl -i --insecure -X POST -H 'cookie: JSESSIONID={uds_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -H 'USER_ID: cs0008' --data @test.json https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/services/{certify_service_unique_id}/distribution/PROD/activate > output_distributeService.txt '''         
            command_output = ExecuteCurlCommand.get_json_output(connection_with_ecm,
                                                                command)
            time.sleep(5)
            log.info(command_output)
        
            source= '/root/output_distributeService.txt'
            destination= r'com_ericsson_do_auto_integration_files/UDS_files/output_distributeService.txt'
            ServerConnection.get_file_sftp(connection_with_ecm, source, destination)
            
            f = open(r'com_ericsson_do_auto_integration_files/UDS_files/output_distributeService.txt','r')
            output=f.readlines()
            log.info(output)
            Report_file.add_line(str(output))
            time.sleep(15) 
            
            if '200 OK' in str(output):
                
                log.info(f'Successfully distributed service.')
                Report_file.add_line(f'Successfully distributed service.')
            else:
                log.info(f'Failed to distribute service.')
                Report_file.add_line(f'Failed to distribute service.')
                connection_with_ecm.close()
                assert False      
        except Exception as e:
            log.error('Error While distributing service ' + str(e))
            Report_file.add_line('Error While distributing service ' + str(e))
            connection_with_ecm.close()
            assert False
        finally:
            connection_with_ecm.close()
            