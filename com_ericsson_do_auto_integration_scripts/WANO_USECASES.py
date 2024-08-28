from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.wano_files_update import *
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import *
import ast



log = Logger.get_logger('WANO_USECASES.py')




def create_wano_service():
    try:

        log.info('Start creating service in WANO ')
        Report_file.add_line('Start creating service in WANO ')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        wano_hostname, wano_user, wano_password = Server_details.get_wano_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        wano_token = Common_utilities.generate_wano_token(Common_utilities,connection)

        service_name = Common_utilities.get_name_with_timestamp(Common_utilities,'SERVICE')
        file_name ='wano_create_service.json'

        update_wano_service_file(file_name,service_name)

        ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/wano_files/' + file_name,
                                       SIT.get_base_folder(SIT) + file_name)

        command = f'''curl --insecure 'https://{wano_hostname}/wano-nbi/wano/v1.1/services' -H 'Cookie: JSESSIONID="{wano_token}"' -H 'Content-Type: application/json' -H 'Accept: application/json' -X POST --data @{file_name}'''

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = command_output[2:-1:1]
        output = ast.literal_eval(command_out)

        status = output['statusMessage']
        if 'SUCCESS' == status:
            activity_Id = output['activityId']
            log.info(f'Successfully  created  service {service_name} with activity id {activity_Id} in WANO ')
            Report_file.add_line(f'Successfully  created  service {service_name} with activity id {activity_Id} in WANO ')
        else:
            log.error(f'Error creating  service {service_name}  in WANO , Please check the Report_file.txt for details')
            assert False


    except Exception as e:

        log.info('Error creating wano service  ' + str(e))
        Report_file.add_line('Error creating wano service' + str(e))
        assert False
    finally:
        connection.close()

