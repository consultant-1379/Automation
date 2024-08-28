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
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_runtime_env_file
from com_ericsson_do_auto_integration_utilities.CURL_UDS_SERVICE_TEMPLATE_CREATION import CurlUdsSTCreation as get_cmd

log = Logger.get_logger('UDS_GENERIC_OPERATIONS.py')


class UDS_GENERIC:

    def onboard_uds_vfcs(self, vfc_type, file_name, key_name_to_update, MD5_code):

        try:
            log.info(f'Start onboarding vfc of type {vfc_type} ')
            Report_file.add_line(f'Start onboarding vfc of type {vfc_type} ')

            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username,
                                                            uds_password, 'master')

            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                            SIT.get_base_folder(SIT) + file_name)

            command = f'''curl --insecure -X POST -H 'Accept: */*' -H 'Content-MD5:{MD5_code}' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token};HTTP_IV_USER=cs0008; USER_ID=cs0008; HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; HTTP_CSP_LASTNAME=Santana; HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources -d @{file_name}'''

            Report_file.add_line('vfc curl command ' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)


            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            if "requestError" in command_out or not command_out:
                if "resource already exists" in command_out:
                    log.info(f'vfc of type {vfc_type} already exists in UDS')
                    Report_file.add_line(f'vfc of type {vfc_type} already exists in UDS')
                    vfc_id = Server_details.get_onboarded_vfc_id(Server_details, vfc_type)
                    return vfc_id

                else:
                    log.error(
                        f'Request Error onboarding vfc of type {vfc_type} , check command output for more details')
                    Report_file.add_line(f'Request Error onboarding vfc of type {vfc_type} , check command output for more details')
                    assert False
            else:
                output = ast.literal_eval(command_out)
                log.info('Fetching out unique id from command out ')
                vfc_id = output['uniqueId']
                log.info(f'vfc id for type {vfc_type} is {vfc_id}')
                Report_file.add_line(f'vfc id for type {vfc_type} is {vfc_id}')
                update_runtime_env_file(key_name_to_update, vfc_id)
                return vfc_id


        except Exception as e:
            log.error(f'Error onboarding vfc of type {vfc_type} ' + str(e))
            Report_file.add_line(f'Error onboarding vfc of type {vfc_type} ' + str(e))
            assert False

        finally:
            connection.close()

    def certify_uds_vfcs(self, vfc_type, vfc_id, key_name_to_update):

        try:
            log.info(f'Start certify vfc of type {vfc_type} ')
            Report_file.add_line(f'Start certify vfc of type {vfc_type} ')

            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username,
                                                            uds_password, 'master')

            command = f'''curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token};HTTP_IV_USER=cs0008; USER_ID=cs0008; HTTP_CSP_FIRSTNAME=Carlos; HTTP_CSP_EMAIL=csantana@sdc.com; HTTP_CSP_LASTNAME=Santana; HTTP_IV_REMOTE_ADDRESS=0.0.0.0; HTTP_CSP_WSTYPE=Intranet; EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{vfc_id}/lifecycleState/certify --data '{'"userRemarks":"Certified"'}{"'"}'''

            Report_file.add_line('certify vfc curl command ' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)


            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            if "requestError" in command_out or not command_out:
                if "resource already exists" in command_out:
                    log.info(f'certify vfc of type {vfc_type} already exists in UDS')
                    Report_file.add_line(f'certify vfc of type {vfc_type} already exists in UDS')
                    certify_vfc_id = Server_details.get_certified_vfc_id(Server_details, vfc_type)
                    return certify_vfc_id

                else:
                    log.error(f'Request Error certify vfc of type {vfc_type} , check command output for more details')
                    Report_file.add_line(f'Request Error certify vfc of type {vfc_type} , check command output for more details')
                    assert False
            else:
                output = ast.literal_eval(command_out)
                log.info('Fetching out unique id from command out ')
                certify_vfc_id = output['uniqueId']
                log.info(f'certify vfc id for type {vfc_type} is {certify_vfc_id}')
                Report_file.add_line(f' certify vfc id for type {vfc_type} is {certify_vfc_id}')
                update_runtime_env_file(key_name_to_update, certify_vfc_id)
                return certify_vfc_id


        except Exception as e:
            log.error(f'Error certify vfc of type {vfc_type} ' + str(e))
            Report_file.add_line(f'Error certify vfc of type {vfc_type} ' + str(e))
            assert False

        finally:
            connection.close()

    def add_vfc_to_vf_composition(self, vfc_type, file_name, vf_unique_id, key_name_to_update):
        try:
            log.info(f'Start to add {vfc_type} to VF composition')
            Report_file.add_line(f'Start to add {vfc_type} to VF composition')

            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username,
                                                            uds_password, 'master')

            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                            SIT.get_base_folder(SIT) + file_name)

            command = f'''curl -i --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008;HTTP_CSP_FIRSTNAME=Carlos;HTTP_CSP_EMAIL=csantana@sdc.com;HTTP_CSP_LASTNAME=Santana;HTTP_IV_REMOTE_ADDRESS=0.0.0.0;HTTP_CSP_WSTYPE=Intranet;EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{vf_unique_id}/resourceInstance -d @{file_name}'''

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

            global capabilities_unique_id, requirements_unique_id
            if '201 Created' in command_output:
                json_start_index = command_out.find('{"capabilities"')

                if json_start_index == -1:
                    log.error('Command output is not as expected , please check the output ')
                    assert False

                command_out = command_out[json_start_index::]
                output = ast.literal_eval(command_out)
                log.info('Fetching out unique id from command out ')

                composition_unique_id = output['uniqueId']
                log.info(f'composition unique id for {vfc_type} is {composition_unique_id}')
                Report_file.add_line(f'composition unique id is for {vfc_type} is {composition_unique_id}')
                update_runtime_env_file(key_name_to_update, composition_unique_id)
                if vfc_type == 'CERTIFY_NETWORK_SERVICE':
                    capabilities_unique_id = output["capabilities"]["tosca.capabilities.Node"][0]["uniqueId"]
                    update_runtime_env_file('UDS_CAPABILITIES_UNIQUE_ID', capabilities_unique_id)
                    requirements_unique_id = output["requirements"]["tosca.capabilities.Node"][0]["uniqueId"]
                    update_runtime_env_file('UDS_REQUIREMENTS_UNIQUE_ID', requirements_unique_id)
                    requirements_owner_id = output["requirements"]["tosca.capabilities.Node"][0]["ownerId"]
                    return composition_unique_id, capabilities_unique_id, requirements_unique_id,requirements_owner_id
                return composition_unique_id

            elif '500 Internal Server Error' in command_output:
                log.info(f'Already Added {vfc_type} to VF Composition')
                Report_file.add_line(f'Already Added {vfc_type} to VF Composition')

                if vfc_type == 'CERTIFY_NETWORK_SERVICE':
                    unique_id_from_adding_ns_composition, capabilities_unique_id, requirements_unique_id = Server_details.get_add_vfc_composition_ids(
                        Server_details)
                    return unique_id_from_adding_ns_composition, capabilities_unique_id, requirements_unique_id
                else:
                    unique_id_from_adding_epg_composition = Server_details.get_add_epg_vfc_composition_id(
                        Server_details)
                    return unique_id_from_adding_epg_composition
            elif '404 Not Found' in command_output:
                log.info(f'Please do check ceritfy_vfc_id or created_vf_id value  for {vfc_type}')
                Report_file.add_line(f'Please do check ceritfy_vfc_id or created_vf_id value  for {vfc_type}')
                assert False
            else:
                log.info(f'Error while adding {vfc_type} to VF composition')
                assert False



        except Exception as e:
            log.error('Error While adding VFC to VF composition' + str(e))
            Report_file.add_line('Error While adding VFC to VF composition' + str(e))
            assert False

        finally:
            connection.close()

    def onboard_the_template(self, type, file_name, MD5_code, vf_unique_id):
        try:
            log.info(f'Start to onboard the template for {type}')
            Report_file.add_line(f'Start to onboard the template for {type}')

            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username,
                                                            uds_password, 'master')

            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                            SIT.get_base_folder(SIT) + file_name)

            command = get_cmd.onboard_config_template(uds_hostname, uds_token, file_name, vf_unique_id, MD5_code)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            command_out = command_output[2:-1:1]
            if '200 OK' in command_output:
                log.info(f'Successfully on boarded the {type} template')
                Report_file.add_line(f'Successfully onboarded the {type} template')
            else:
                log.info(f'Failed to onboard the {type} template')
                Report_file.add_line(f'Failed to onboard the {type} template')
                assert False

        except Exception as e:
            log.info('Error While onboarding the template')
            Report_file.add_line('Error While onboarding the template')
            assert False

    def create_inputs(self, file_name, vf_unique_id,type):
        try:
            log.info(f'Start to create to input for {type}')
            Report_file.add_line(f'Start to create to input for {type}')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username,
                                                            uds_password, 'master')

            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                            SIT.get_base_folder(SIT) + file_name)

            command = f'''curl -i --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008;HTTP_CSP_FIRSTNAME=Carlos;HTTP_CSP_EMAIL=csantana@sdc.com;HTTP_CSP_LASTNAME=Santana;HTTP_IV_REMOTE_ADDRESS=0.0.0.0;HTTP_CSP_WSTYPE=Intranet;EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{vf_unique_id}/create/inputs -d @{file_name}'''

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            command_out = command_output[2:-1:1]
            if '100 Continue' in command_output:
                log.info(f'Successfully created the inputs for {type}')
                Report_file.add_line(f'Successfully created the inputs for {type} ')
            else:
                log.info(f'Failed to create the input for {type}')
                Report_file.add_line(f'Failed to create the input for {type} ')
                assert False

        except Exception as e:
            log.info('Error while Creating inputs')
            Report_file.add_line('Error while Creating inputs')
            assert False

    def add_properties(self, type, file_name, vf_unique_id, unique_composition_id):
        try:
            log.info(f'Start to add properties for {type}')
            Report_file.add_line(f'Start to add properties for {type}')
            uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            uds_token = Common_utilities.generate_uds_token(Common_utilities, connection, uds_hostname, uds_username,
                                                            uds_password, 'master')

            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/UDS_files/' + file_name,
                                            SIT.get_base_folder(SIT) + file_name)

            # command = f'''curl --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008;HTTP_CSP_FIRSTNAME=Carlos;HTTP_CSP_EMAIL=csantana@sdc.com;HTTP_CSP_LASTNAME=Santana;HTTP_IV_REMOTE_ADDRESS=0.0.0.0;HTTP_CSP_WSTYPE=Intranet;EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{VF_UNIQUE_ID}/create/inputs -d @{file_name}'''

            command = f'''curl -i --insecure -X POST -H 'Accept: */*' -H 'Content-Type: application/json' -H 'Cookie: JSESSIONID={uds_token}; HTTP_IV_USER=cs0008; USER_ID=cs0008;HTTP_CSP_FIRSTNAME=Carlos;HTTP_CSP_EMAIL=csantana@sdc.com;HTTP_CSP_LASTNAME=Santana;HTTP_IV_REMOTE_ADDRESS=0.0.0.0;HTTP_CSP_WSTYPE=Intranet;EPService=portal' https://{uds_hostname}/sdc1/feProxy/rest/v1/catalog/resources/{vf_unique_id}/resourceInstance/{unique_composition_id}/properties -d @{file_name}'''

            command_output = ExecuteCurlCommand.get_json_output(connection, command)

            command_out = command_output[2:-1:1]
            if '200 OK' in command_output:
                log.info(f'Successfully created the inputs for {type}')
                Report_file.add_line(f'Successfully created the inputs for {type} ')
            else:
                log.info(f'Failed to add properties for {type}')
                Report_file.add_line(f'Failed to add properties for {type} ')
                assert False

        except Exception as e:
            log.info('Error while adding properties')
            Report_file.add_line('Error while adding properties')
            assert False
