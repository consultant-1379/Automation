# pylint: disable=C0103,C0114,C0115,R0205,R0914,W0212,R1705,R1710,W0612,R0915,W0703,R0913,C0209
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
import time
import ast
import base64
from packaging import version
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('ExecuteCurlCommand.py')


class ExecuteCurlCommand(object):
    @staticmethod
    def get_ecm_token(connection, is_ecm=False):
        """
        Returns token
        @param connection:
        @param is_ecm:
        @return: token
        """
        log.info('Generating token in the host blade server using the  curl command  ')

        epis_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        if is_ecm:
            tenant_id = 'ECM'
            ecm_gui_username = 'ecmadmin'
            ecm_gui_password = 'CloudAdmin123'

        else:
            tenant_id = epis_data._EPIS__tenant_name
            ecm_gui_username = ecm_host_data._Ecm_core__ecm_gui_username
            ecm_gui_password = ecm_host_data._Ecm_core__ecm_gui_password

        auth_basic = base64.b64encode(bytes(ecm_gui_username + ':' + ecm_gui_password, encoding='utf-8'))
        decoded_auth_basic = auth_basic.decode('utf-8')
        log.info(decoded_auth_basic)

        curl = ('''curl -X POST \
            --header 'Authorization:Basic {}' \
            --header 'TenantId:{}' \
            --insecure  https://{}:443/ecm_service/tokens'''.format(
            decoded_auth_basic, tenant_id, core_vm_hostname
        ))

        log.info('Command to create token: %s',curl)

        command = curl
        log.info('Curl command for auth token : %s',command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        log.info('Token Generation curl output: %s',command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        request_status = output['status']['reqStatus']

        if 'SUCCESS' in request_status:

            token_string = ast.literal_eval(command_output[2:-1:1])
            token = token_string['status']['credentials']
            log.info('Generated token in the host blade server using the  curl command:  %s', token)
            return token

        elif 'ERROR' in request_status:

            command_error = output['status']['msgs'][0]['msgText']
            log.error(command_error)
            log.info('Error executing curl command for token generation')
            connection.close()
            assert False

    @staticmethod
    def get_json_output(connection, command, base_folder=""):
        """
        Executes command and returns its output
        @param connection:
        @param command:
        @return:
        """
        if not base_folder:
            base_folder = SIT.get_base_folder(SIT)
        command = f'cd {base_folder}; {command}'
        command_output = ''
        log.info('Executing curl command: %s',command)
        Report_file.add_line('Executing curl command : ' + command)
        retry = 0
        while retry <= 4:
            stdin, stdout, stderr = connection.exec_command(command)

            command_output = str(stdout.read())
            log.info('command output: %s',command_output)
            Report_file.add_line('command output : ' + command_output)
            command_out = command_output[2:-1:1]

            if 'Service Unavailable' in command_out:
                log.warning('******************  CHECK WITH APPLICATION TEAM ****************************')
                log.warning('Error while running curl on APPLICATION  : %r', command_out)
                log.warning('*********************  SERVICE UNAVAILABLE  ******************************')
                log.info('Going to retry the command')
                log.info('waiting 30 seconds to retry....')
                time.sleep(30)
                retry = retry + 1
            elif 'Service Temporarily Unavailable' in command_out:
                log.warning('*********************  CHECK WITH APPLICATION TEAM ************************')
                log.warning('Error while running curl on APPLICATION  : %r', command_out)
                log.warning('*********************  SERVICE TEMPORARILY UNAVAILABLE  *******************')
                log.info('Going to retry the command')
                log.info('waiting 30 seconds to retry....')
                time.sleep(30)
                retry = retry + 1
            elif 'Internal Server Error' in command_out:
                log.warning('******************  CHECK WITH APPLICATION TEAM ****************************')
                log.warning('Error while running curl on APPLICATION : %s', command_out)
                log.warning('*********************  INTERNAL SERVER ERROR  ******************************')
                log.info('Going to retry the command')
                log.info('waiting 30 seconds to retry....')
                time.sleep(30)
                retry = retry + 1
            elif 'Access Denied' in command_out:
                log.warning('Access denied in output %s', command_out)
                log.info('Going to retry the command')
                log.info('waiting 60 seconds to retry....')
                time.sleep(60)
                retry = retry + 1
            elif 'Invalid token' in command_out:
                log.warning('Invalid Token in output %s ', command_out)
                log.info('Curl command with invalid token: %s ', command)
                data = ExecuteCurlCommand.get_sliced_command_output(command_output)
                log.info('DATA: %s',data)
                data = ast.literal_eval(data)
                invalid_token = data['status']['credentials']
                log.info('Generating new token due to invalid token')
                new_token = ExecuteCurlCommand.get_ecm_token(connection)
                log.info('New token generated is: %s', new_token)
                command = command.replace(invalid_token, new_token)
                log.info('Going to retry the command with new token %s ', command)
                retry = retry + 1
            else:
                retry = 999

        if retry == 5:
            log.error('Problem with command output from application ,please check output in report file for details..')
            log.error('Terminating the job after 5 retry')
            assert False

        return command_output

    @staticmethod
    def get_sliced_command_output(command_output):
        """
        Formats command output
        @param command_output:
        @return:
        """
        command_out = command_output[2:-1:1]
        try:

            command_out = command_out.replace('true', 'True')
            command_out = command_out.replace('false', 'False')
            command_out = command_out.replace('null', "''")
            command_out = command_out.replace('\\"', '\"')
        except Exception as error:
            log.error('ERROR while updating the command_output %s', str(error))

        return command_out

    @staticmethod
    def get_output_replace_braces(command_output):
        """
        Formats command output
        @param command_output:
        @return:
        """
        command_out = command_output[2:-1:1]
        try:

            command_out = command_out.replace('true', 'True')
            command_out = command_out.replace('false', 'False')
            command_out = command_out.replace('null', '""')
            command_out = command_out.replace('\\', '')
            command_out = command_out.replace('"{', '{')
            command_out = command_out.replace('}"', '}')

        except Exception as error:
            log.error('ERROR while updating the command_output %s', str(error))

        return command_out

    @staticmethod
    def curl_onboard_so_template(
        so_version, file_name, form_name, so_host_name, so_token, artifact_type, param=None
    ):
        """
        Returns curl command to onboard artifacts
        @return:
        @param artifact_type: type of artifact to be onboarded
        @param so_version:
        @param file_name: file to be onboarded
        @param form_name: template to be onboarded
        @param so_host_name: host name
        @param so_token: token
        @param param: optional parameter e.g. -i
        @return: curl command
        """

        if so_version <= version.parse('1.2.1860'):
            curl = (
                f'curl --insecure --form "file=@{file_name}" --form "name={form_name}"'
                f' https://{so_host_name}/onboarding/eso/v1.0/service-models'
                f' -H "Cookie: JSESSIONID={so_token}"'
            )
        else:
            if so_version <= version.parse('2.10.0-37'):
                api_version = 'v1'
            elif so_version <= version.parse('2.11.0-551'):
                api_version = 'v2'
            else:
                api_version = 'v3'

            curl = (
                f'curl --insecure {param} --form "type={artifact_type}" --form "file=@{file_name}"'
                f' --form "name={form_name}" https://{so_host_name}/onboarding/{api_version}/artifacts'
                f' -H "Cookie: JSESSIONID={so_token}"'
            )
        return curl
