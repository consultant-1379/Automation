# pylint: disable=C0302,C0103,C0301,C0412,E0602,W0621,C0411,R0915,E0602,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612
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

'''
Created on 28 Jan 2021


@author: zsyapra
'''
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import get_sol_dummy_service_id, action_status_so, \
    poll_status_so
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_vnflaf_yaml_scalefiles
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import *
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_scripts.SCALE_HEAL import *

import ast

log = Logger.get_logger('SO_DUMMY_SCALE.py')


class SO_DUMMY_SCALE:

    def get_so_dummy_service_name(self, connection):
        try:
            log.info('Start to fetch so dummy Service  name from runtime file')
            Report_file.add_line('Start to fetch so dummy Service name from runtime file')
            environment = Server_details.ecm_host_blade_env(Server_details)
            data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
            source = r'/root/' + 'run_time_' + environment + '.json'
            ServerConnection.get_file_sftp(connection, source, data_file)
            global name
            name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, 'ONBOARD_PACKAGE')
            return name

        except Exception as e:
            log.error('Failed to fetch SO Dummy Service name %s',  str(e))
            Report_file.add_line('Failed to fetch SO Dummy Service name' + str(e))
            assert False

    def update_the_so_dummy_scale_yaml_file(self, file_path, file_name):
        update_vnflaf_yaml_scalefiles(file_path, file_name, '', '', 'SO-DUUMY-SCALE')

    def fetch_scale_action_id(self, output):
        try:
            log.info('Start to fetch Action id')
            Report_file.add_line('Start to fetch Action id')

            action_refs = output['actionRefs']
            # log.info('Action Refs List - '+action_refs)
            if len(action_refs) == 0:
                log.info('Action refs list is empty')
                Report_file.add_line('Action refs list is empty')
                assert False
            else:
                action_refs.sort(key=int)
                action_id = action_refs[-1]
                Report_file.add_line('Action Id -' + action_id)
                return action_id
        except Exception as e:
            log.error('Failed to fetch action id' + str(e))
            Report_file.add_line('Failed to fetch action id' + str(e))
            assert False

    def scale_operations(self, file_name, option):
        try:
            log.info(f'Start SO Dummy {option}')
            Report_file.add_line(f'Start SO Dummy {option}')

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(Server_details)
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
            so_host_name = sit_data._SIT__so_host_name
            is_vm_vnfm = sit_data._SIT__is_vm_vnfm

            token_user = 'staging-user'
            token_password = 'Testing12345!!'
            token_tenant = 'staging-tenant'

            file_path = 'com_ericsson_do_auto_integration_files/'
            yaml_file_name = 'vnflafecm_cee-env.yaml'

            self.update_the_so_dummy_scale_yaml_file(self, file_path, yaml_file_name)

            if 'TRUE' == is_vm_vnfm:
                Report_file.add_line(f'Nested connection open for {option}')

                dir_connection = get_VMVNFM_host_connection()
                source_filepath = file_path + yaml_file_name
                ServerConnection.put_file_sftp(dir_connection, source_filepath,
                                                r'/home/' + vm_vnfm_director_username + '/' + yaml_file_name)

                source = '/home/{}/{}'.format(vm_vnfm_director_username, yaml_file_name)
                destination = '/vnflcm-ext/current/vnf_package_repo/vnflafecm/HOT/Resources/EnvironmentFiles/' + yaml_file_name
                transfer_director_file_to_vm_vnfm(dir_connection, source, destination)

                log.info('waiting 2 seconds to transfer the file to VM-VNFM ')
                time.sleep(2)
                dir_connection.close()
                Report_file.add_line(f'Nested connection closed for {option}')

            else:
                log.info('So Dummy - LCM Connection ')
                lcm_connection = ServerConnection.get_connection(lcm_server_ip, lcm_username,
                                                                 lcm_password)
                sftp = lcm_connection.open_sftp()
                sftp.put(file_path + yaml_file_name, '/home/cloud-user/' + yaml_file_name)
                sftp.close()

                command = f'sudo -i cp /home/cloud-user/{yaml_file_name} /vnflcm-ext/current/vnf_package_repo/vnflafecm/HOT/Resources/EnvironmentFiles/{yaml_file_name}'

                lcm_connection.exec_command(command, get_pty=True)
                time.sleep(2)
                lcm_connection.close()
                log.info('So Dummy - LCM Connection close')

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/' + file_name,
                                            SIT.get_base_folder(SIT) + file_name)

            sol_dummy_service_name = self.get_so_dummy_service_name(self, connection)

            so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                          token_password, token_tenant)

            service_id = get_sol_dummy_service_id(connection, sol_dummy_service_name, so_token, so_host_name)

            # storing the id as it will be used in polling so service state
            sit_data._SIT__network_service_id = service_id

            log.info(f'Service id is {service_id}')
            command = '''curl -k -X PATCH -H 'cookie: JSESSIONID={}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d @{} https://{}/orchestration/v1/services/{}'''.format(
                so_token, file_name, so_host_name, service_id)
            Report_file.add_line('Command  ' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

            Report_file.add_line('Command out ' + command_out)

            log.info('Going to check action state')

            output = ast.literal_eval(command_out)

            action_id = self.fetch_scale_action_id(self, output)

            timeout = 50

            log.info('waiting 10 sec for service state to be in progress ')
            time.sleep(10)

            action_status_so(connection, so_token, so_host_name, action_id)

            connection.close()

            operations = ["Scale-In", "Scale-Out"]
            if option in operations:
                tosca_scale_service_state_check()
            else:
                # it will check service status , using a new fresh connection
                poll_status_so()



        except Exception as e:
            log.error(f'Error in SO Dummy {option}' + str(e))
            Report_file.add_line(f'Error in SO Dummy {option}' + str(e))
            assert False


    def so_dummy_scale_in(self):
        file_name = 'scaleIn_Dummy_sol005.json'
        self.scale_operations(self, file_name, "Scale-In")

    def so_dummy_scale_out(self):
        file_name = 'scaleOut_Dummy_sol005.json'
        self.scale_operations(self, file_name, "Scale-Out")

    def so_dummy_heal(self):
        start_heal('SO-DUMMY-HEAL')
