'''
Created on 18 Oct 2018

@author: eiaavij
'''
# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under  which the
# program(s) have been supplied.
#
# ********************************************************************


import base64
import bcrypt
from datetime import datetime
import os
import random
import hashlib
import yaml
import json
import zlib
import ast
import time

from tabulate import tabulate

from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection, \
    get_vmvnfm_pod_cmd, transfer_director_file_to_vm_vnfm
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand

log = Logger.get_logger('Common_utilities.py')


class Common_utilities(object):
    """
    class for all the common utility methods
    """

    def get_eocm_connection_token(self):
        """
        create eocm connection and token
        """
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        return connection, token

    def get_name_with_random_plaintext(self, name):

        dateTimeObj = datetime.now()

        return '{}{}{}'.format(name, str(random.randint(0, 999)), str(dateTimeObj.date()).replace('-', ''))

    def get_name_with_timestamp(self, name):

        dateTimeObj = datetime.now()
        return '{}-{}-{}'.format(name, str(dateTimeObj.date()), str(dateTimeObj.time()).split('.')[0].replace(':', '-'))

    def generate_MD5_checksum_for_json(self, file_path):
        # data -- it is the content of file for which we need to get MD5 code
        log.info('Generating MD5 code for file ' + file_path)
        with open(file_path, "r") as json_file:
            json_data = json.load(json_file)

        data = json.dumps(json_data)

        generated_MD5_code = base64.b64encode(hashlib.md5(data.encode('utf-8')).hexdigest().encode('utf-8')).decode(
            'utf-8')
        log.info("Generated MD5 code :: " + generated_MD5_code)
        return generated_MD5_code

    def generate_base64_code_for_yamlfile(self, yaml_file_path):

        log.info('Generating base64 code for file ' + yaml_file_path)
        with open(yaml_file_path, "r") as yaml_file:
            yaml_data = yaml.load(yaml_file)

        data = str(yaml_data)
        auth_basic = base64.b64encode(bytes(data, encoding='utf-8'))
        base64_code = auth_basic.decode('utf-8')
        Report_file.add_line(f"base64 code for file {yaml_file_path} : {base64_code}")
        return base64_code

    def generate_base64_code_for_jsonfile(self, json_file_path):

        log.info('Generating base64 code for file ' + json_file_path)
        with open(json_file_path, "r") as json_file:
            data = json.load(json_file)

        json_string = json.dumps(data)
        auth_basic = base64.b64encode(bytes(json_string, encoding='utf-8'))
        base64_code = auth_basic.decode('utf-8')
        log.info(f"base64 code for file %s : %s", json_file_path, base64_code)
        return base64_code

    def get_vnf_lcm_version(self, connection):

        log.info('going to fetch VNF-LCM version')

        command = 'vnflcm version'

        stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

        command_output = str(stdout.read())[2:-3:]

        log.info('command output : ' + command_output)

        version_list = command_output.split('\\r\\')

        version = version_list[0].split(':')[1].strip()

        log.info('Version of deployed VNF-LCM is : ' + version)

        return version

    def get_bcrypt_encrypted_password(self, password, salt_rounds, prefix):

        data = password.encode()

        enc_passwd = bcrypt.hashpw(data, bcrypt.gensalt(salt_rounds, prefix))

        return enc_passwd.decode('utf-8')

    def fetch_cmdb_password(self):

        log.info('Start fetching the password of cmdb user')

        log.info('going to remove the known_hosts file entry')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        abcd_vm_ip = ecm_host_data._Ecm_core__abcd_vm_ip

        os_command = 'ssh-keygen -R {}'.format(abcd_vm_ip)
        os.system(os_command)

        time.sleep(2)

        username = ecm_host_data._Ecm_core__abcd_vm_username
        password = ecm_host_data._Ecm_core__abcd_vm_password

        abcd_connection = ServerConnection.get_connection(abcd_vm_ip, username, password)

        command = 'cat /ecm-umi/install/.ecm_passwords | grep -i cmdb'
        Report_file.add_line('command : ' + command)
        stdin, stdout, stderr = abcd_connection.exec_command(command)
        command_output = stdout.read()
        command_out = command_output.decode("utf-8")
        Report_file.add_line('command output : ' + command_out)
        output = command_out.split()
        password = output[1][1:-1:]

        abcd_connection.close()
        log.info('Finished fetching the password of cmdb user')

        return password

    # def get_AES_encripted_password(self,passwd):

    #     data = passwd.encode()
    #     key = get_random_bytes(16)
    #     cipher = AES.new(key, AES.MODE_CBC)
    #     ct_bytes = cipher.encrypt(pad(data, AES.block_size))
    #     init_vector = b64encode(cipher.iv).decode('utf-8')
    #     password = b64encode(ct_bytes).decode('utf-8')

    #     return password,init_vector

    def get_auth_basic(self, username, password):

        auth_basic = base64.b64encode(bytes(username + ':' + password, encoding='utf-8'))
        decoded_auth_basic = auth_basic.decode('utf-8')
        log.info(decoded_auth_basic)
        return decoded_auth_basic

    def crc(self, fileName):
        prev = 0
        for eachLine in open(fileName, "rb"):
            prev = zlib.crc32(eachLine, prev)
        return "%X" % (prev & 0xFFFFFFFF)

    def get_vendor_session_id(self, connection, vendor_ip):

        log.info('Start fetching session id for vendor operations')
        Report_file.add_line('Start fetching session id for vendor operations')

        file_name = 'vendor_credentials.json'

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        command = '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' -d @{} 'https://{}:8443/ecde-gateway/v1/vendors/session{}'''.format(
            file_name, vendor_ip, "'")

        log.info('ECDE vendor session id command : ' + command)
        Report_file.add_line('ECDE vendor session id command : ' + command)

        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('ECDE vendor session id curl output' + command_output)

        output = ast.literal_eval(command_output[2:-1:1])

        request_status = output['requestStatus']

        if 'SUCCESS' in request_status:

            sessionId = output['sessionId']
            log.info('Generated sessionid for ECDE vendor ' + sessionId)
            Report_file.add_line('Generated sessionid for ECDE vendor ' + sessionId)
            return sessionId

        else:

            log.error('Error in curl response generating session Id for ECDE vendor ' + command_output)

            Report_file.add_line('Error in curl response generating session Id for ECDE vendor ' + command_output)
            connection.close()
            assert False

    def get_uds_token(self):
        uds_hostname, uds_username, uds_password = Server_details.get_uds_host_data(Server_details)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        uds_token = self.generate_uds_token(self, connection, uds_hostname, uds_username,
                                            uds_password, 'master')
        return uds_hostname, uds_token, connection

    def generate_uds_token(self, connection, uds_host_name, user, password, tenant):
        log.info('Generate UDS token')
        Report_file.add_line('Generating UDS token..')
        command = '''curl --insecure -X  POST -H "Content-Type: application/json" -H "X-login: {}" -H "X-password: {}" -H "X-tenant: {}" https://{}/auth/v1/login'''.format(
            user, password, tenant, uds_host_name)
        log.info('UDS token curl ' + command)
        Report_file.add_line('UDS token curl ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('UDS token command output ' + command_output)
        if 'Name or service not known' in command_output:
            log.error('Check the UDS hostname , error while fetching the UDS token')
            Report_file.add_line('Check the UDS hostname , error while fetching the UDS token')
            connection.close()
            assert False
        elif 'Error=' in command_output:
            log.error('Check username or password , error while fetching the UDS token')
            Report_file.add_line('Check username or password , error while fetching the UDS token')
            connection.close()
            assert False
        elif 'Network is unreachable' in command_output:
            log.error('Check the UDS Network , error while connecting with UDS')
            Report_file.add_line('Check the UDS hostname , error while fetching the UDS token')
            connection.close()
            assert False
        elif 'Internal Server Error' in command_output:
            log.error('*********************CHECK WITH UDS TEAM  ******************************')
            log.error('Check the UDS Network , error while generating token , Error : ' + command_output)
            Report_file.add_line('Check the UDS Network , error while generating token , Error : ' + command_output)
            log.error('*********************INTERNAL SERVER ERROR ******************************')
            connection.close()
            assert False
        else:
            uds_token = command_output[2:-1:1]

            if uds_token:

                log.info('UDS token generated is ' + uds_token)
                Report_file.add_line('UDS token id  is ' + uds_token)
                return uds_token

            else:

                log.error('UDS token not generated ERROR :  ' + uds_token)
                Report_file.add_line('UDS token not generated ' + uds_token)
                assert False

    def generate_so_token(self, connection, so_host_name, user, password, tenant):

        log.info('Generate SO token')
        Report_file.add_line('Generating SO token..')
        command = '''curl --insecure -X  POST -H "Content-Type: application/json" -H "X-login: {}" -H "X-password: {}" -H "X-tenant: {}" https://{}/auth/v1/login'''.format(
            user, password, tenant, so_host_name)
        log.info('So token curl ' + command)
        Report_file.add_line('So token curl ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('So token command output ' + command_output)
        if 'Name or service not known' in command_output:
            log.error('Check the SO hostname , error while fetching the so token')
            Report_file.add_line('Check the SO hostname , error while fetching the so token')
            connection.close()
            assert False
        elif 'Error=' in command_output:
            log.error('Check username or password , error while fetching the so token')
            Report_file.add_line('Check username or password , error while fetching the so token')
            connection.close()
            assert False
        elif 'Network is unreachable' in command_output:
            log.error('Check the SO Network , error while connecting with SO')
            Report_file.add_line('Check the SO hostname , error while fetching the so token')
            connection.close()
            assert False
        elif 'Internal Server Error' in command_output:
            log.error('*********************CHECK WITH SO TEAM  ******************************')
            log.error('Check the SO Network , error while generating token , Error : ' + command_output)
            Report_file.add_line('Check the SO Network , error while generating token , Error : ' + command_output)
            log.error('*********************INTERNAL SERVER ERROR ******************************')
            connection.close()
            assert False
        elif 'userMessage' in command_output:
            log.error('*********************CHECK WITH SO TEAM  ******************************')
            log.error('Unexpected response from application: %s', str(command_output))
            connection.close()
            assert False
        else:
            so_token = command_output[2:-1:1]

            if so_token:

                log.info('SO token generated is ' + so_token)
                Report_file.add_line('So token id  is ' + so_token)
                return so_token

            else:

                log.error('SO token not generated  ' + so_token)
                Report_file.add_line('So token not generated ' + so_token)
                assert False

    def generate_wano_token(self, connection):

        log.info('Generate wano  token')
        Report_file.add_line('Generating wano  token..')

        wano_hostname, wano_user, wano_password = Server_details.get_wano_details(Server_details)

        command = f'''curl --insecure -X  POST -H "Content-Type: application/json" -H "X-login: {wano_user}" -H 'X-password: {wano_password}'  https://{wano_hostname}/auth/v1'''

        Report_file.add_line('wano token curl ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('wano token command output ' + command_output)
        if 'Name or service not known' in command_output:
            log.error('Check the wano hostname , error while fetching the wano token')
            Report_file.add_line('Check the wano hostname , error while fetching the wano token')
            connection.close()
            assert False
        elif 'Error=' in command_output:
            log.error('Check username or password , error while fetching the wano token')
            Report_file.add_line('Check username or password , error while fetching the wano token')
            connection.close()
            assert False
        elif 'Network is unreachable' in command_output:
            log.error('Check the WANO Network , error while connecting with WANO')
            Report_file.add_line('Check the WANO hostname , error while fetching the WANO token')
            connection.close()
            assert False
        elif 'Internal Server Error' in command_output:
            log.error('*********************CHECK WITH WANO TEAM  ******************************')
            log.error('Check the WANO Network , error while generating token , Error : ' + command_output)
            Report_file.add_line('Check the WANO Network , error while generating token , Error : ' + command_output)
            log.error('*********************INTERNAL SERVER ERROR ******************************')
            connection.close()
            assert False
        else:
            wano_token = command_output[2:-1:1]

            if wano_token:

                log.info('WANO token generated is ' + wano_token)
                Report_file.add_line('WANO token id  is ' + wano_token)
                return wano_token

            else:

                log.error('SO token not generated  ' + wano_token)
                Report_file.add_line('So token not generated ' + wano_token)
                assert False

    def get_evnfm_token(self, connection):

        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        log.info('Generate EVNFM token')
        Report_file.add_line('Generating EVNFM token..')
        command = '''curl --insecure -X POST -H "Content-Type: application/json" -H "X-login: {}" -H "X-password: {}" https://{}/auth/v1'''.format(
            evnfm_username, evnfm_password, evnfm_hostname)
        log.info('EVNFM token curl ' + command)
        Report_file.add_line('EVNFM token curl ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('EVNFM token command output ' + command_output)
        if 'Name or service not known' in command_output:
            log.error('Check the EVNFM hostname , error while fetching the so token')
            Report_file.add_line('Check the EVNFM hostname , error while fetching the so token')
            connection.close()
            assert False
        elif 'Error=' in command_output:
            log.error('Check username or password , error while fetching the EVNFM token')
            Report_file.add_line('Check username or password , error while fetching the EVNFM token')
            connection.close()
            assert False
        elif 'Network is unreachable' in command_output:
            log.error('Check the EVNFM Network , error while connecting with EVNFM')
            Report_file.add_line('Check the EVNFM hostname , error while fetching the EVNFM token')
            connection.close()
            assert False
        elif 'Internal Server Error' in command_output:
            log.error('*********************CHECK WITH EVNFM TEAM  ******************************')
            log.error('Check the EVNFM Network , error while generating token , Error : ' + command_output)
            Report_file.add_line('Check the EVNFM Network , error while generating token , Error : ' + command_output)
            log.error('*********************INTERNAL SERVER ERROR ******************************')
            connection.close()
            assert False
        else:
            evnfm_token = command_output[2:-1:1]

            if evnfm_token:

                log.info('EVNFM token generated is ' + evnfm_token)
                Report_file.add_line('EVNFM token id  is ' + evnfm_token)
                return evnfm_token

            else:

                log.error('EVNFM token not generated  ' + evnfm_token)
                Report_file.add_line('EVNFM token not generated ' + evnfm_token)
                assert False

    def generate_enm_token(self, connection, enm_hostname, enm_username, enm_password):

        log.info('Generate ENM token')
        Report_file.add_line('Genrating ENM token..')
        command = '''curl -k --request POST "https://{}/login" -d IDToken1="{}" -d IDToken2="{}" --cookie-jar cookie.txt'''.format(
            enm_hostname, enm_username, enm_password)
        log.info('ENM token curl ' + command)
        Report_file.add_line('ENM token curl ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        source = r'/root/cookie.txt'
        dest = 'cookie.txt'
        ServerConnection.get_file_sftp(connection, source, dest)

        num = "~"
        search = open("cookie.txt")
        for line in search:
            if num in line:
                enm_token = line.split("~", 1)[1].strip()

        Report_file.add_line('ENM token command output ' + enm_token)

        log.info('ENM token generated is ' + enm_token)
        Report_file.add_line('ENM token id  is ' + enm_token)
        return enm_token

    def authToken(self, connection, core_vm_ip, is_ecm=False):

        token = ExecuteCurlCommand.get_ecm_token(connection, is_ecm)
        return token

    def sync_proj_authToken(self, connection, core_vm_hostname):

        log.info('Generating token in the host blade server using the  curl command  ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

        tenant_id = EPIS_data._EPIS__sync_tenant_name
        tenant_username = EPIS_data._EPIS__sync_tenant_username
        tenant_password = EPIS_data._EPIS__sync_tenant_password

        auth_basic = base64.b64encode(bytes(tenant_username + ':' + tenant_password, encoding='utf-8'))
        decoded_auth_basic = auth_basic.decode('utf-8')
        log.info(decoded_auth_basic)

        curl = '''curl -X POST --header 'Authorization:Basic {}' --header 'TenantId:{}'  --insecure  https://{}:443/ecm_service/tokens'''.format(
            decoded_auth_basic, tenant_id, core_vm_hostname)
        command = curl
        Report_file.add_line('Curl command for auth token : ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('Token Generation curl output' + command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            token_string = ast.literal_eval(command_output[2:-1:1])
            token = token_string['status']['credentials']
            log.info('Generated token in the host blade server using the  curl command:  ' + token)
            Report_file.add_line('Token Generated' + token)

            return token

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error(command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for token generation')
            connection.close()
            assert False

    def podauthToken(self, connection, core_vm_hostname):

        log.info('Generating token in the host blade server using the  curl command  ')

        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        tenant_id = EPIS_data._EPIS__tenant_name
        ecm_gui_username = ecm_host_data._Ecm_core__ecm_gui_username
        ecm_gui_password = ecm_host_data._Ecm_core__ecm_gui_password
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        # core_vm_ip is replaced with core_vm_hostname due to token issue for Ipv6 address
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        auth_basic = base64.b64encode(bytes(ecm_gui_username + ':' + ecm_gui_password, encoding='utf-8'))
        decoded_auth_basic = auth_basic.decode('utf-8')
        log.info(decoded_auth_basic)
        cmd = f"curl -X POST --header 'Authorization:Basic {decoded_auth_basic}' " \
              f"--header 'TenantId:{tenant_id}' --insecure  https://{core_vm_hostname}:443/ecm_service/tokens"

        command = get_vmvnfm_pod_cmd(cmd)
        Report_file.add_line('Curl command for auth token : ' + command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('Token Generation curl output' + command_output)
        output = ast.literal_eval(command_output[2:-1:1])
        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            token_string = ast.literal_eval(command_output[2:-1:1])
            token = token_string['status']['credentials']
            log.info('Generated token in the host blade server using the  curl command:  ' + token)
            Report_file.add_line('Token Generated' + token)

            return token

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error(command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for token generation')
            assert False

    def orderReqStatus(self, connection, token, core_vm_hostname, order_id, wait_time):

        time_out = 3600
        log.info('Time out for this order status is ' + str(time_out) + ' Seconds')

        curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' https://{}/ecm_service/v2/orders/{}'''.format(
            token, core_vm_hostname, order_id)

        command = curl
        Report_file.add_line('Executing the order id curl command  ' + command)

        while (time_out != 0):

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('command output  ' + command_output)
            command_out = command_output[2:-1:1]
            try:

                command_out = command_out.replace('true', 'True')
                command_out = command_out.replace('false', 'False')
                command_out = command_out.replace('\\"', '\"')
                command_out = command_out.replace('null', '""')

            except:

                log.error('ERROR while updating the command_output')

            output = ast.literal_eval(command_out)

            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:

                orderReqStatus = output['data']['order']['orderReqStatus']

                if 'SUBCOM' in orderReqStatus:
                    log.info('Order Status is inProgress ' + order_id)
                    log.info('Waiting ' + str(wait_time) + ' seconds for completion of order ' + order_id)
                    time_out = time_out - wait_time
                    time.sleep(wait_time)

                elif 'COM' in orderReqStatus or 'WARN' in orderReqStatus:

                    return True, output

                elif 'ERR' in orderReqStatus:

                    if 'orderMsgs' in str(output):
                        msgText = output['data']['order']['orderMsgs'][0]['msgText']
                        log.info('Order Status is failed ' + order_id + msgText)
                        Report_file.add_line('Order Status is failed ' + order_id + msgText)
                    else:
                        log.info('Order Status is failed ' + order_id)
                        Report_file.add_line('Order Status is failed ' + order_id)

                    return False, output

                else:
                    log.info('Order Status is inProgress ' + order_id)
                    log.info('Waiting ' + str(wait_time) + ' seconds for completion of order ' + order_id)
                    time_out = time_out - wait_time
                    time.sleep(wait_time)

            elif 'ERROR' in requestStatus:

                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for orderReqStatus ' + command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command for orderReqStatus')
                return False, output

        if time_out == 0:
            log.info(
                'Order status polling is timed out after 60 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            Report_file.add_line(
                'Order status polling is timed out after 60 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            connection.close()
            assert False

    def accesstoken_dcgw(self, connection, core_vm_hostname):

        ecm_host_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        activation_vm_ip = ecm_host_data._Ecm_PI__activation_vm_ip
        log.info('Generating access token for DCGW  ')
        command = 'cat /app/ecm/tools/users.properties | grep -i act'
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = stdout.read()
        string_data = command_output.decode("utf-8")
        output = string_data.split()
        map1 = {}
        for word in output:
            first, last = word.split('=')
            print(last.strip("'"))
            map1[first] = last.strip("'")
        curl = '''curl -X POST --user 'ECM:{}' -d 'username={}&password={}&grant_type=password' -k https://{}:8383/oam/oauth/token'''.format(
            map1['act_secret'], map1['act_user'], map1['act_password'], activation_vm_ip)
        command = curl
        Report_file.add_mesg('Step', 'Executing the curl command to create token', command)
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        output = ast.literal_eval(command_output[2:-1:1])

        if "error" in output.keys():
            log.info('Access Token generated failed:  ' + command_output)
            Report_file.add_line('Access Token generated failed' + command_output)
            assert False

        else:
            token = output['access_token']
            log.info('Generated token in the host blade server using the  curl command:  ' + token)
            Report_file.add_line('Token Generated' + token)
            return token

    def ovforderReqStatus(self, connection, token, core_vm_hostname, ovf_package_name, wait_time):

        log = Logger.get_logger('Common_utilities')
        time_out = 3600
        log.info('Time out for this order status is ' + str(time_out) + ' Seconds')

        curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DOVFPKG%7C{}{}'''.format(
            token, core_vm_hostname, ovf_package_name, "'")

        command = curl
        Report_file.add_line('Executing the order id curl command  ' + command)

        while (time_out != 0):

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('command output  ' + command_output)
            command_out = command_output[2:-1:1]
            try:

                command_out = command_out.replace('true', 'True')
                command_out = command_out.replace('false', 'False')
                command_out = command_out.replace('\\"', '\"')
                command_out = command_out.replace('null', '""')
            except:

                log.error('ERROR while updating the command_output')

            output = ast.literal_eval(command_out)

            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:

                orderReqStatus = output['data']['orders'][0]['orderReqStatus']
                order_id = output['data']['orders'][0]['id']
                log.info('Order id for ' + ovf_package_name + ' is  ' + order_id)

                if 'COM' in orderReqStatus or 'WARN' in orderReqStatus:

                    return True, output

                elif 'ERR' in orderReqStatus:

                    if 'orderMsgs' in str(output):
                        msgText = output['data']['order']['orderMsgs'][0]['msgText']
                        log.info('Order Status is failed ' + order_id + msgText)
                        Report_file.add_line('Order Status is failed ' + order_id + msgText)
                    else:
                        log.info('Order Status is failed ' + order_id)
                        Report_file.add_line('Order Status is failed ' + order_id)

                    return False, output

                else:
                    log.info('Order Status is inProgress ' + ovf_package_name)
                    log.info('Waiting ' + str(wait_time) + ' seconds for completion of order ' + ovf_package_name)
                    time_out = time_out - wait_time
                    time.sleep(wait_time)

            elif 'ERROR' in requestStatus:

                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for orderReqStatus ' + command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command for orderReqStatus')
                return False, output

        if time_out == 0:
            log.info(
                'Order status polling is timed out after 20 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            Report_file.add_line(
                'Order status polling is timed out after 15 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            connection.close()
            assert False

    def scale_healorderReqStatus(self, connection, command, wait_time, operation):

        log = Logger.get_logger('Common_utilities')
        time_out = 1200
        log.info('Time out for this order status is ' + str(time_out) + ' Seconds')

        Report_file.add_line('Executing the order id curl command  ' + command)
        count = 0
        while (time_out != 0):

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('command output  ' + command_output)
            command_out = command_output[2:-1:1]
            try:

                command_out = command_out.replace('true', 'True')
                command_out = command_out.replace('false', 'False')
                command_out = command_out.replace('\\"', '\"')
                command_out = command_out.replace('null', '""')
            except:

                log.error('ERROR while updating the command_output')

            output = ast.literal_eval(command_out)

            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:
                data_dict_content = output['data']
                if not data_dict_content:
                    if count == 2:
                        log.info(
                            'The Heal order was not generated with in 210 seconds,Hence making the job status as Failure')
                        Report_file.add_line(
                            'The Heal order was not generated with in 210 seconds,Hence making the job status as Failure')
                    assert False
                    log.info('waiting for ' + str(wait_time) + ' seconds to kick off HEAL order')
                    Report_file.add_line('waiting for ' + str(wait_time) + ' seconds to kick off HEAL order')
                    time_out = time_out - wait_time
                    time.sleep(wait_time)
                    count = count + 1
                else:
                    orderReqStatus = output['data']['orders'][0]['orderReqStatus']
                    order_id = output['data']['orders'][0]['id']
                    Report_file.add_line('Order id of Heal - ' + order_id)

                    if 'COM' in orderReqStatus:

                        return True, output

                    elif 'ERR' in orderReqStatus:

                        if 'orderMsgs' in str(output):
                            msgText = output['data']['order']['orderMsgs'][0]['msgText']
                            log.info('Order Status is failed ' + order_id + msgText)
                            Report_file.add_line('Order Status is failed ' + order_id + msgText)
                        else:
                            log.info('Order Status is failed ' + order_id)
                            Report_file.add_line('Order Status is failed ' + order_id)

                        return False, output

                    else:
                        log.info('Order Status is inProgress ' + operation + ' for the order - ' + order_id)
                        log.info('Waiting ' + str(
                            wait_time) + ' seconds for completion of order ' + operation + ' for ' + order_id + ' order id')
                        time_out = time_out - wait_time
                        time.sleep(wait_time)

            elif 'ERROR' in requestStatus:

                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for orderReqStatus ' + command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command for orderReqStatus')
                return False, output

        if time_out == 0:
            log.info(
                'Order status polling is timed out after 20 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            Report_file.add_line(
                'Order status polling is timed out after 15 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            connection.close()
            assert False

    def transfer_wrapperfile_into_vmvnfm(self, file_name):

        try:
            log.info('Start transferring ' + file_name + ' to pod  path VnfdWrapperFiles directory ')
            Report_file.add_line('Start transferring ' + file_name + ' to pod VnfdWrapperFiles directory')

            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            directory_server_ip = ecm_host_data._Ecm_core__vm_vnfm_director_ip
            directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username

            nested_conn = get_VMVNFM_host_connection()
            log.info('Transferring ' + file_name + ' to director server ip ' + directory_server_ip)

            ServerConnection.put_file_sftp(nested_conn,
                                           r'com_ericsson_do_auto_integration_files/vnflaf/Resources/VnfdWrapperFiles/' + file_name,
                                           r'/home/' + directory_server_username + '/' + file_name)

            source = '/home/' + directory_server_username + '/' + file_name
            destination = '/vnflcm-ext/current/vnf_package_repo/vnflaf/Resources/VnfdWrapperFiles'

            log.info('Transferring ' + file_name + ' file to eric-vnflcm-service pod ')

            transfer_director_file_to_vm_vnfm(nested_conn, source, destination)

            time.sleep(20)

        except Exception as e:

            log.error('Error transferring ' + file_name + ' file to pod VnfdWrapperFiles directory ' + str(e))
            Report_file.add_line(
                'Error transferring ' + file_name + ' file to pod  VnfdWrapperFiles directory' + str(e))
            assert False

        finally:
            nested_conn.close()

    def ecm_order_create_status(self, connection, token, core_vm_hostname, wait_time, vnf_package_name):

        time_out = 600
        log.info('Time out for this order status is ' + str(time_out) + ' Seconds')

        curl = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/orders?$filter=searchTag%3DVNFPKG%7C{}{}'''.format(
            token, core_vm_hostname, vnf_package_name, "'")

        command = curl
        Report_file.add_line('Executing the order id curl command  ' + command)

        while (time_out != 0):

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('command output  ' + command_output)
            output = command_output[2:-1:1]
            try:

                output = output.replace('true', 'True')
                output = output.replace('false', 'False')
                output = output.replace('\\"', '\"')
                output = output.replace('null', '""')

            except:

                log.error('ERROR while updating the command_output')

            if 'SUCCESS' in output:

                if 'id' in output:

                    log.info('Order Creation completed ')
                    return True, output

                else:
                    log.info('Order creation still in Progress ')
                    log.info('Waiting ' + str(wait_time) + ' seconds for creation of order ')
                    time_out = time_out - wait_time
                    time.sleep(wait_time)

            elif 'ERROR' in output:

                log.error('Error executing curl command for ecm create order status ')
                Report_file.add_line()
                Report_file.add_line('Error executing curl command for ecm create order status')
                return False, output

        if time_out == 0:
            log.info('Order creation is timed out after 10 minutes, Please check order details in ECM ')
            Report_file.add_line('Order creation is timed out after 10 minutes, Please check order details in ECM ')
            connection.close()
            assert False

    def take_back_up_of_a_file(self, connection, file_name, back_up_file_name, source_file_abs_path,
                               dest_file_abs_path):
        try:
            log.info('Start to take back up of a ' + file_name + ' file.')
            Report_file.add_line('Start to take back up of a ' + file_name + ' file.')
            source_file_path = source_file_abs_path + file_name
            dest_file_path = dest_file_abs_path + back_up_file_name

            command = 'cp ' + source_file_path + ' ' + dest_file_path
            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('backup file command output ' + command_output)

        except Exception as e:
            log.error('Error while taking backup of file ' + str(e))
            Report_file.add_line('Error while taking back up of a file ' + str(e))
            assert False

    def execute_curl_command(self, connection, command):
        try:
            Report_file.add_line('command  Input: ' + command)

            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            try:

                command_out = command_out.replace('\\"', '\"')

            except:
                log.error('ERROR while updating the command_output')

            output = ast.literal_eval(command_out)

            Report_file.add_line('json Output : ' + str(output))
            return output

        except Exception as e:
            log.error('Error while executing ' + command + '' + str(e))
            Report_file.add_line('Error while executing ' + command + '' + str(e))
            assert False

    def NSorderReqStatus(self, connection, token, core_vm_hostname, order_id, wait_time):

        time_out = 3600
        warn_suborder_status_count = 0
        log.info('Time out for this order status is ' + str(time_out) + ' Seconds')

        command = '''curl --insecure "https://{}/ecm_service/v2/orders/{}" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
            core_vm_hostname, order_id, token)

        # command = curl
        Report_file.add_line('Executing the order id curl command  ' + command)

        while (time_out != 0):

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('command output  ' + command_output)
            command_out = command_output[2:-1:1]
            try:

                command_out = command_out.replace('true', 'True')
                command_out = command_out.replace('false', 'False')
                command_out = command_out.replace('\\"', '\"')
                command_out = command_out.replace('null', '""')


            except:

                log.error('ERROR while updating the command_output')

            output = ast.literal_eval(command_out)

            requestStatus = output['status']['reqStatus']

            if 'SUCCESS' in requestStatus:

                orderReqStatus = output['data']['order']['orderReqStatus']

                if 'SUBCOM' in orderReqStatus:
                    log.info('Order Status is inProgress ' + order_id)
                    log.info('Waiting ' + str(wait_time) + ' seconds for completion of order ' + order_id)
                    time_out = time_out - wait_time
                    time.sleep(wait_time)

                elif 'COM' in orderReqStatus:

                    return True, output

                elif 'WARN' in orderReqStatus:
                    order_items = output['data']['order']['orderItems']
                    for item in order_items:
                        if 'deployVnfPackage' in item or 'terminateVnf' in item:
                            if 'deployVnfPackage' not in item:
                                suborder = item['terminateVnf']['order']
                            else:
                                suborder = item['deployVnfPackage']['order']
                            if suborder['status'] == 'ERR':
                                Report_file.add_line('Sub Order Status is failed')
                                warn_suborder_status_count = warn_suborder_status_count + 1
                            else:
                                Report_file.add_line('Sub Order Status is completed')

                    if warn_suborder_status_count != 0:
                        return False, output
                    else:
                        return True, output



                elif 'ERR' in orderReqStatus:

                    if 'orderMsgs' in str(output):
                        msgText = output['data']['order']['orderMsgs'][0]['msgText']
                        log.info('Order Status is failed ' + order_id + msgText)
                        Report_file.add_line('Order Status is failed ' + order_id + msgText)
                    else:
                        log.info('Order Status is failed ' + order_id)
                        Report_file.add_line('Order Status is failed ' + order_id)

                    return False, output

                else:
                    log.info('Order Status is inProgress ' + order_id)
                    log.info('Waiting ' + str(wait_time) + ' seconds for completion of order ' + order_id)
                    time_out = time_out - wait_time
                    time.sleep(wait_time)

            elif 'ERROR' in requestStatus:

                command_error = output['status']['msgs'][0]['msgText']
                log.error('Error executing curl command for orderReqStatus ' + command_error)
                Report_file.add_line(command_error)
                Report_file.add_line('Error executing curl command for orderReqStatus')
                return False, output

        if time_out == 0:
            log.info(
                'Order status polling is timed out after 60 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            Report_file.add_line(
                'Order status polling is timed out after 60 minutes, Please check order details in ECM and order status is  : ' + orderReqStatus)
            connection.close()
            assert False

    def fetch_attribute_from_runtimefile(self, attribute_name):
        try:
            log.info('Start to fetch ' + attribute_name + ' from runtime file')
            Report_file.add_line('Start to fetch ' + attribute_name + ' from runtime file')
            environment = Server_details.ecm_host_blade_env(Server_details)
            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
            source = r'/root/' + 'run_time_' + environment + '.json'
            ServerConnection.get_file_sftp(connection, source, data_file)
            onboard_package_name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, attribute_name)
            log.info('Fetched Attribute - %s', str(onboard_package_name))
            return onboard_package_name
        except Exception as e:
            log.info('Error while fetching ' + attribute_name + ' from runtime file ' + str(e))
            Report_file.add_line('Error while fetching ' + attribute_name + ' from runtime file ' + str(e))
            assert False
        finally:
            connection.close()

    def clean_up_rpm_packages(self, connection, rpm_name):
        try:
            sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
            is_vm_vnfm = sit_data._SIT__is_vm_vnfm

            if 'TRUE' == is_vm_vnfm:

                ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
                vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
                directory_server_username = ecm_host_data._Ecm_core__vm_vnfm_director_username

                log.info('Starting removal of rpm package ' + rpm_name)
                Report_file.add_line('Starting removal of rpm package ' + rpm_name)
                cmd = f"rm -rf {rpm_name}"
                command = get_vmvnfm_pod_cmd(cmd)
                Report_file.add_line('command for rpm clean-up  : ' + command)
                stdin, stdout, stderr = connection.exec_command(command)
                command_output = str(stdout.read())
                log.info(command_output)
                Report_file.add_line('command output :' + command_output)

                log.info('Starting removal of rpm package ' + rpm_name + ' on eccd')
                Report_file.add_line('Starting removal of rpm package ' + rpm_name + ' on eccd')
                path = '/home/' + directory_server_username
                cmd = 'cd {};rm -rf {}'.format(path, rpm_name)
                Report_file.add_line('command for rpm clean-up  : ' + cmd)
                stdin, stdout, stderr = connection.exec_command(cmd)
                command_output = str(stdout.read())
                log.info(command_output)
                Report_file.add_line('command output :' + command_output)

            else:

                log.info('Starting removal of rpm package ' + rpm_name)
                Report_file.add_line('Starting removal of rpm package ' + rpm_name)
                command = 'rm -rf {}'.format(rpm_name)
                Report_file.add_line('command for rpm clean-up  : ' + command)
                stdin, stdout, stderr = connection.exec_command(command)
                command_output = str(stdout.read())
                log.info(command_output)
                Report_file.add_line('command output :' + command_output)

        except Exception as e:

            log.error('Error removal of rpm package ' + rpm_name + '\n Error: ' + str(e))
            Report_file.add_line('Error removal of rpm package ' + rpm_name + '\n Error: ' + str(e))

    def create_artifact_prop_file(self, packages, pkg_type):
        pkg_details = Common_utilities.get_vnfd_package_details(Common_utilities, packages, pkg_type)
        pkg_versions = ", ".join(item["pkg_version"] for item in pkg_details.values())
        property_key = f'{pkg_type}_version'
        Common_utilities.update_property_file(Common_utilities, pkg_versions, property_key)

    def get_vnfd_package_details(self, packages, pkg_type):
        log.info("Start creating artifact property file data for packages %s", str(packages))
        package_details = {}
        for pkg_id in packages:
            if pkg_type in ['CCRC_INSTALL', 'CCRC_UPGRADE']:
                evnfm_hostname = Ecm_core.get_evnfm_hostname(Ecm_core)
                ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
                connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
                evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

                curl = f"curl --insecure -H 'cookie: JSESSIONID={evnfm_token}' " \
                       f"https://{evnfm_hostname}/vnfm/onboarding/api/v1/packages/{pkg_id}"
                command_output = ExecuteCurlCommand.get_json_output(connection, curl)
                command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
                output = ast.literal_eval(command_out)
                if output:
                    pkg_name = output["descriptorModel"]["topology_template"]["node_templates"]["CCRC"]["type"]
                    package_details[pkg_id] = {'pkg_name': pkg_name,
                                               'pkg_version': output['descriptorVersion']}

            else:
                core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
                ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
                connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
                token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
                curl = f"curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: " \
                       f"application/json' --header 'AuthToken:{token}' https://{core_vm_hostname}/ecm_service/" \
                       f"vnfpackages/{pkg_id}?%24data=%7B%22operationInputParamsSchema%22%3Atrue%2C%22vnfPackage" \
                       f"ChangePolicies%22%3Atrue%2C%22modifiableAttributesSchema%22%3Atrue%2C%22vnfConfigurable" \
                       f"PropertiesSchema%22%3Atrue%2C%22scalingAspects%22%3Atrue%7D"

                command_output = ExecuteCurlCommand.get_json_output(connection, curl)
                command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
                output = ast.literal_eval(command_out)
                if output.get('data'):
                    pkg_name = output['data']['vnfPackage']['fileName']
                    package_details[pkg_id] = {'pkg_name': pkg_name,
                                               'pkg_version': output['data']['vnfPackage']['softwareVersion']}
        return package_details

    def update_property_file(self, pkg_versions, property_key, file_name=None):
        property_info = f'{property_key}={pkg_versions}'
        log.info('Start updating of artifact.properties file with data: %s', property_info)
        if not file_name:
            file_name = 'artifact.properties'
        with open(file_name, "w") as file:
            file.write(property_info)
        log.info('%s file updated successfully', file_name)

    @staticmethod
    def tabulate_data(data, headers, tablefmt='grid'):
        log.info('\n%s', tabulate(data, headers, tablefmt, showindex='always'))
