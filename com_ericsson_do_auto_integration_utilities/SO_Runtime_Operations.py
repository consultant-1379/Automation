from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities import Json_file_handler
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
import ast
log = Logger.get_logger('SO_Runtime_Operations.py')


def get_so_service_name(connection, attribute_name):
    try:
        log.info('Start to fetch SO Service  name from runtime file')
        Report_file.add_line('Start to fetch SO Service name from runtime file')
        environment = Server_details.ecm_host_blade_env(Server_details)
        data_file = r'com_ericsson_do_auto_integration_files/run_time_' + environment + '.json'
        source = r'/root/' + 'run_time_' + environment + '.json'
        ServerConnection.get_file_sftp(connection, source, data_file)
        name = Json_file_handler.get_json_attr_value(Json_file_handler, data_file, attribute_name)
        return name

    except Exception as e:
        log.error('Failed to fetch SO Service name' + str(e))
        Report_file.add_line('Failed to fetch SO Service name' + str(e))
        assert False


def fetch_action_id(output):
    try:
        log.info('Start to fetch Action id')
        Report_file.add_line('Start to fetch Action id')

        if 'userMessage' in output.keys():
            log.error(output['userMessage'])
            Report_file.add_line(output['userMessage'])
            assert False

        action_refs = output['actionRefs']

        if len(action_refs) == 0:
            log.info('Action refs list is empty')
            Report_file.add_line('Action refs list is empty')
            assert False
        else:
            action_refs.sort(key=int)
            action_id = action_refs[-1]
            Report_file.add_line(f'Action Id - {action_id}')
            return action_id

    except Exception as e:
        log.error('Failed to fetch action id' + str(e))
        Report_file.add_line('Failed to fetch action id ' + str(e))
    assert False


def get_so_service_id(connection, service_name, so_token, so_host):
    try:

        log.info('Start to get Service Id')
        Report_file.add_line('Start to get Service Id')

        command = f'''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{so_token}"' https://{so_host}/orchestration/v1/services'''

        Report_file.add_line(f'Executing command : {command}')
        log.info(f'Executing command : {command}')
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        total_items = len(output)

        if total_items != 0:
            for item in output:
                if item['name'] == service_name:
                    return item['id']

        else:
            log.info('NO Active services available in Service Orchestration gui')
            Report_file.add_line('NO Active services available in Service Orchestration gui')
            assert False

    except Exception as e:
        log.error('Failed to get service id: ' + str(e))
        Report_file.add_line('Failed to get service id: ' + str(e))
        assert False

