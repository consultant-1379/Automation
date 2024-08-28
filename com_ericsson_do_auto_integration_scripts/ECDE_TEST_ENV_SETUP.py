'''
Created on Sep 04, 2020

@author: emaidns
'''
# pylint: disable=C0116,C0301,C0103,W0703

import json
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.ECDE_files_update import (
    update_aat_tool_file,
    update_aat_testsuite_file,
)
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_scripts.ECDE_NODE_PREREQUISITES import (
    get_AAT_tool_id,
    get_AAT_testcase_id,
)

log = Logger.get_logger('ECDE_TEST_ENV_SETUP.py')


def create_ecde_aat_tool():
    try:
        log.info('Start creating AAT tool in ECDE Test tools ')
        Report_file.add_line('Start creating AAT tool in ECDE Test tools ')

        file_name = 'create_aat.json'

        ecde_aat_ip, ecde_aat_user, ecde_aat_password = Server_details.ecde_AAT_details(Server_details)

        update_aat_tool_file(file_name, ecde_aat_ip, ecde_aat_user, ecde_aat_password)

        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
            r'/root/' + file_name,
        )

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json'  --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/test-head-catalogs' -d @{file_name}'''
        Report_file.add_line('command :  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '200 OK' in command_output:

            log.info('Successfully created AAT tool in ECDE Test tools ')
            Report_file.add_line('Successfully created AAT tool in ECDE Test tools ')
        elif 'error.recordWithSameName' in command_output:
            log.info('AAT tool is already exists')
            Report_file.add_line('AAT tool is already exists')
        else:
            log.error('Error creating AAT tool in ECDE Test tools %s', command_output)
            Report_file.add_line(
                'Error creating AAT tool in ECDE Test tools , check the above comamnd output for details '
            )
            assert False
        global ecde_aat_id
        ecde_aat_id = get_AAT_tool_id(connection, ecde_fqdn, auth_basic)

    except Exception as e:
        log.error('Error creating AAT tool in ECDE Test tools %s', str(e))
        Report_file.add_line('Error creating AAT tool in ECDE Test tools ' + str(e))
        assert False

    finally:
        connection.close()


def add_testcase_to_aat_tool():
    try:
        log.info('Start creating testcase in ECDE AAT tool ')
        Report_file.add_line('Start creating testcase in ECDE AAT tool ')

        file_name = 'create_testcase_aat.json'

        ecde_aat_ip, ecde_aat_user, ecde_aat_password = Server_details.ecde_AAT_details(Server_details)

        update_aat_tool_file(file_name, ecde_aat_ip, ecde_aat_user, ecde_aat_password, ecde_aat_id)

        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
            r'/root/' + file_name,
        )

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json'  --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/testcases' -d @{file_name}'''
        Report_file.add_line('command :  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '201 Created' in command_output:
            log.info('Successfully created testcase in ECDE AAT tool ')
            Report_file.add_line('Successfully created testcase in ECDE AAT tool ')
        elif 'error.recordWithSameName' in command_output:
            log.info('testcase in AAT tool is already exists in ECDE admin ')
            Report_file.add_line('testcase in AAT tool is already exists in ECDE admin ')
        else:
            log.error('Error creating testcase in ECDE AAT tool %s', command_output)
            Report_file.add_line(
                'Error creating testcase in ECDE AAT tool , check the above comamnd output for details '
            )
            assert False

        global ecde_testcase_id
        ecde_testcase_id = get_AAT_testcase_id(connection, ecde_fqdn, auth_basic)

    except Exception as e:
        log.error('Error creating AAT tool in ECDE Test tools %s', str(e))
        Report_file.add_line('Error creating AAT tool in ECDE Test tools ' + str(e))
        assert False

    finally:
        connection.close()


def add_ecde_testsuit():
    try:
        log.info('Start creating self_ping_suite testsuit in ECDE AAT tool ')
        Report_file.add_line('Start creating self_ping_suite testsuit in ECDE AAT tool ')

        file_name = 'create_aat_testsuite.json'

        ecde_aat_ip, ecde_aat_user, ecde_aat_password = Server_details.ecde_AAT_details(Server_details)

        update_aat_testsuite_file(
            file_name, ecde_aat_ip, ecde_aat_user, ecde_aat_password, ecde_aat_id, ecde_testcase_id
        )

        ecde_fqdn, ecde_user, ecde_password = Server_details.ecde_user_details(Server_details, 'admin')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.put_file_sftp(
            connection,
            r'com_ericsson_do_auto_integration_files/ECDE_files/' + file_name,
            r'/root/' + file_name,
        )

        auth_basic = Common_utilities.get_auth_basic(Common_utilities, ecde_user, ecde_password)

        command = f'''curl -i -X POST --insecure --header 'Authorization:Basic {auth_basic}' --header 'Content-Type: application/json'  --header 'Accept: application/json'  'https://{ecde_fqdn}/core/api/test-suites/self_ping_suite' -d @{file_name}'''
        Report_file.add_line('command :  ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '201 Created' in command_output:
            log.info('Successfully created testsuit in ECDE AAT tool ')
            Report_file.add_line('Successfully created testsuite in ECDE AAT tool ')
        elif 'error.testSuiteidexists' in command_output:
            log.info('self_ping_suite testsuit is already exists in ECDE admin ')
            Report_file.add_line('self_ping_suite testsuit is already exists in ECDE admin ')
        else:
            log.error('Error creating testsuite in ECDE AAT tool %s', command_output)
            Report_file.add_line(
                'Error creating testsuite in ECDE AAT tool , check the above comamnd output for details '
            )
            assert False

    except Exception as e:
        log.error('Error creating AAT tool in ECDE Test tools %s', str(e))
        Report_file.add_line('Error creating AAT tool in ECDE Test tools ' + str(e))
        assert False

    finally:
        connection.close()


def clean_ecde_spinnaker():
    try:
        log.info('Start deleting all the TEP pipeline from ecde spinnaker')
        Report_file.add_line('Start deleting all the TEP pipeline from ecde spinnaker')

        (
            ecde_spinnaker_ip,
            ecde_spinnaker_user,
            ecde_spinnaker_password,
        ) = Server_details.ecde_spinnaker_details(Server_details)

        connection = ServerConnection.get_connection(
            ecde_spinnaker_ip, ecde_spinnaker_user, ecde_spinnaker_password
        )

        command = 'spin pipeline list --application ecde-app'

        Report_file.add_line('Command to list all the TEP : ' + command)

        stdin, stdout, stderr = connection.exec_command(command)
        command_output = stdout.read()
        command_out = command_output.decode("utf-8")
        Report_file.add_line('Command output  : ' + command_out)

        if len(command_out) == 3:
            log.info('No Pipelines to delete , ECDE Spinnaker is cleaned up ..')
            Report_file.add_line('No Pipelines to delete , ECDE Spinnaker is cleaned up ..')
        else:
            pipeline_name = []
            piplei_obj = json.loads(command_out)

            log.info('getting pipeline names')

            for items in piplei_obj:
                pipeline_name.append(items['name'])
                log.info(items['name'])

            log.info('deleting pipelines')

            for pipeline in pipeline_name:
                log.info(f'Start deleting pipeline %s', pipeline)
                delete = 'spin pipeline delete --name %s --application ecde-app' % pipeline
                connection.exec_command(delete)
                log.info(f'Success deleting pipeline %s', pipeline)

            log.info('ALL PIPELINES REMOVED')
            Report_file.add_line('ALL PIPELINES REMOVED')

    except Exception as e:
        log.error('Error deleting all the TEP pipeline from ecde spinnaker %s', str(e))
        Report_file.add_line('Error deleting all the TEP pipeline from ecde spinnaker ' + str(e))
        assert False

    finally:
        connection.close()
