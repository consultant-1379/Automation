'''
Created on 30 April 2020


@author: eiaavij
'''
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization

log = Logger.get_logger('General_files_update.py')


def update_register_cism(file, nested_conn, register_url):
    try:
        log.info('updating %s file', file)
        file_name = r'com_ericsson_do_auto_integration_files/' + file

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        cnf_vnfm_id = sit_data._SIT__cnf_vnfm_id

        config_file = 'config'
        encoded_client_certificate_data = Json_file_handler.get_any_attribute_yaml_value(Json_file_handler, config_file,
                                                                                         ['users', 0, 'user'],
                                                                                         'client-certificate-data')
        encoded_client_key_data = Json_file_handler.get_any_attribute_yaml_value(Json_file_handler, config_file,
                                                                                 ['users', 0, 'user'],
                                                                                 'client-key-data')

        certificate_command = 'echo ' + encoded_client_certificate_data + ' | base64 --decode'
        key_command = 'echo ' + encoded_client_key_data + ' | base64 --decode'

        stdin, stdout, stderr = nested_conn.exec_command(certificate_command)

        output = str(stdout.read())
        client_certificate_data = output[2:-1]
        client_certificate_data = client_certificate_data.replace('\\n', '\n')

        stdin, stdout, stderr = nested_conn.exec_command(key_command)

        output = str(stdout.read())
        client_key_data = output[2:-1]
        client_key_data = client_key_data.replace('\\n', '\n')

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["cism", "cismConfiguration"], 'url',
                                               register_url)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["cism", "cismConfiguration"],
                                               'clientCertificate', client_certificate_data)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["cism", "cismConfiguration"],
                                               'clientCertificateKey', client_key_data)
        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ['cism'], 'vnfmId', cnf_vnfm_id)

        log.info('end updating %s file', file)

    except Exception as e:

        log.error('Error while updating %s %s', file, str(e))
        Report_file.add_line('Error while updating file')
        assert False


def update_modify_cism(file, register_url):
    try:
        log.info('updating modify_register_CISM.json file')
        file_name = r'com_ericsson_do_auto_integration_files/' + file

        Json_file_handler.update_any_json_attr(Json_file_handler, file_name, ["cismConfiguration"], 'url',
                                               register_url)

        log.info('end updating modify_register_CISM.json file')

    except Exception as e:

        log.error('Error while updating modify_register_CISM.json %s', str(e))
        assert False


def update_ccrc_scale_file(file_name, operation, aspect_id):
    try:
        log.info('updating aspect id  in ' + file_name)

        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           'type', operation)

        Json_file_handler.modify_attribute(Json_file_handler, r'com_ericsson_do_auto_integration_files/' + file_name,
                                           'aspectId', aspect_id)
    except Exception as e:

        log.error('Error while updating ccrc scale file ' + str(e))
        Report_file.add_line('Error while updating ccrc scale file ')
        assert False
