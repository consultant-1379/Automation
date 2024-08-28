from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_agat.AGAT_utilities import cnf_scale
import ast

log = Logger.get_logger('EVNFM_NODE_DEPLOYMENT.py')


def create_vnf_package_resource_id(connection, evnfm_token, software_dir, file):
    try:
        log.info('Creating vnf package resource id ')
        Report_file.add_line('Creating vnf package resource id  ')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname

        path = '/var/tmp/{}/'.format(software_dir)

        curl = '''curl --insecure -H 'Accept: application/json' -H 'cookie: JSESSIONID={}' -X POST https://{}/vnfm/onboarding/api/vnfpkgm/v1/vnf_packages -H 'Content-Type: application/json' --data @{}'''.format(
            evnfm_token, evnfm_hostname, file)

        command = 'cd ' + path + ' ; ' + curl

        Report_file.add_line('vnf package resource id command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        resource_id = output['id']

        return resource_id


    except Exception as e:

        log.info('Error creating vnf package resource id ' + str(e))
        Report_file.add_line('Error creating vnf package resource id ' + str(e))
        assert False


def onboarding_cnf_csar(connection, evnfm_token, software_dir, cnf_package):
    try:

        log.info('onboarding ccrc cnf csar package to create vnfd id ')
        Report_file.add_line('onboarding ccrc cnf csar package to create vnfd id   ')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')

        evnfm_hostname = ecm_host_data._Ecm_core__evnfm_hostname
        resource_id = sit_data._SIT__ccrc_resource_id

        path = '/var/tmp/{}/'.format(software_dir)

        curl = '''curl --insecure -i -X PUT https://{}/vnfm/onboarding/api/vnfpkgm/v1/vnf_packages/{}/package_content -H 'Accept: */*' -H 'Content-Type: multipart/form-data' -H 'cookie: JSESSIONID={}' -F file=@{}'''.format(
            evnfm_hostname, resource_id, evnfm_token, cnf_package)

        command = 'cd ' + path + ' ; ' + curl

        Report_file.add_line('onboarding ccrc cnf csar package command : ' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        Report_file.add_line('onboarding ccrc cnf csar package command output : ' + command_output)

        if 'Continue' in command_output:

            return True

        else:

            return False


    except Exception as e:

        log.info('Error onboarding ccrc cnf csar package to create vnfd id ' + str(e))
        Report_file.add_line('Error onboarding ccrc cnf csar package to create vnfd id ' + str(e))
        assert False


def create_node_vnf_identifier(node_name, file_name):
    try:

        log.info('Start creating vnf identifier for  ' + node_name)
        Report_file.add_line('Start creating vnf identifier for  ' + node_name)

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        curl = '''curl --insecure -X POST https://{}/vnflcm/v1/vnf_instances -H 'Accept: */*' -H 'Content-Type: application/json' -H 'cookie: JSESSIONID={}' --data @{}'''.format(
            evnfm_hostname, evnfm_token, file_name)

        command = curl
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        vnf_identifier_id = output['id']
        vnf_identifier_name = output['vnfInstanceName']

        sit_data._SIT__vnf_identifier_id = vnf_identifier_id

        log.info('VNF Identifier succesfully created with name {} and Id {}'.format(vnf_identifier_name, vnf_identifier_id))

        Report_file.add_line('VNF Identifier succesfully created with name {} and Id {}'.format(vnf_identifier_name,
                                                                                                vnf_identifier_id))


    except Exception as e:

        log.info('Error creating vnf identifier  ' + str(e))
        Report_file.add_line('Error creating vnf identifier ' + str(e))
        assert False
    finally:
        connection.close()


def upload_node_ccd_target_cnfig(node_name, file_name, software_dir):
    try:

        log.info('Start Uploading ccd target config for  ' + node_name)
        Report_file.add_line('Start Uploading ccd target config for  ' + node_name)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        curl = '''curl -i --insecure -X POST https://{}/vnfm/wfs/api/lcm/v2/cluster -H 'Accept: */*' -H 'cookie: JSESSIONID={}' -F clusterConfig=@{}'''.format(
            evnfm_hostname, evnfm_token, file_name)

        command = 'cd ' + software_dir + ' ; ' + curl

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '201 Created' in command_output:
            log.info('Finished Uploading ccd target config for  ' + node_name)
            Report_file.add_line('Finished Uploading ccd target config for  ' + node_name)

        elif '409 Conflict' in command_output:
            log.info('ccd target config already uploaded for ' + node_name)
            Report_file.add_line('ccd target config already uploaded for ' + node_name)

        else:
            log.error('Error Uploading ccd target config for  ' + node_name + 'check logs for details')
            assert False

    except Exception as e:

        log.info('Error Uploading ccd target config  ' + str(e))
        Report_file.add_line('Error Uploading ccd target config ' + str(e))
        assert False
    finally:
        connection.close()


def ccrc_node_deploy(node_name, file_name, values_file_name, software_dir, vnf_identifier_id):
    connection = None
    try:

        log.info('Instantiating vnf type  %s', node_name)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        curl = '''curl -i --insecure -X POST https://{}/vnflcm/v1/vnf_instances/{}/instantiate -H 'Accept: */*' -H 'Content-Type: multipart/form-data' -H 'cookie: JSESSIONID={}' -F instantiateVnfRequest=@{} -F valuesFile=@{}'''.format(
            evnfm_hostname, vnf_identifier_id, evnfm_token, file_name, values_file_name)

        command = 'cd ' + software_dir + ' ; ' + curl
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '202 Accepted' in command_output:
            log.info('Order has been submitted for vnf deployment  %s', node_name)
        else:
            log.error('Error while Order submission for vnf deployment  %s ', node_name)
            assert False

    except Exception as e:
        log.info('Error instantiate vnf type %s', str(e))
        assert False
    finally:
        connection.close()


def upgrade_ccrc_node_package(node_name, file_name, vnf_identifier_id):
    try:

        log.info('Start upgrading  vnf type  ' + node_name)
        Report_file.add_line('Start upgrading  vnf type   ' + node_name)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        curl = f'''curl -i --insecure -X POST https://{evnfm_hostname}/vnflcm/v1/vnf_instances/{vnf_identifier_id}/change_vnfpkg   -H 'Accept: */*' -H 'Content-Type: application/json' -H 'cookie: JSESSIONID={evnfm_token}' --data @{file_name}'''

        command = curl
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        if '202 Accepted' in command_output:
            log.info('Order has been submitted for vnf upgrade  ' + node_name)
            Report_file.add_line('Order has been submitted for vnf upgrade  ' + node_name)
        else:
            log.error('Error while Order submission for vnf upgrade  ' + node_name + 'check logs for details')
            assert False

    except Exception as e:

        log.error('Error upgrade vnf type  ' + str(e))
        Report_file.add_line('Error upgrade vnf type ' + str(e))
        assert False
    finally:
        connection.close()


def get_ccrc_vnf_details(node_name, vnf_identifier_id):
    try:

        log.info('get details for  vnf type  ' + node_name)
        Report_file.add_line('get details for  vnf type   ' + node_name)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        curl = '''curl --insecure -X GET https://{}/vnflcm/v1/vnf_instances/{} -H 'cookie: JSESSIONID={}{}'''.format(evnfm_hostname, vnf_identifier_id, evnfm_token, "'")

        command = curl

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        aspect_id = output["instantiatedVnfInfo"]["scaleStatus"][0]["aspectId"]

        log.info('aspect id for scale : ' + aspect_id)

        return aspect_id

    except Exception as e:

        log.error('Error get details for vnf ' + str(e))
        Report_file.add_line('Error get details for vnf ' + str(e))
        assert False
    finally:
        connection.close()


def ccrc_node_scale_operation(file_name, operation, node_name, vnf_identifier_id):
    try:

        log.info(f'Start {operation}  for  vnf type {node_name} ')
        Report_file.add_line(f'Start {operation}  for  vnf type {node_name} ')

        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        command_output = cnf_scale(vnf_identifier_id, file_name, evnfm_hostname, evnfm_username, evnfm_password)
        output = str(command_output)

        if '202' in output:
            log.info('Order has been submitted for vnf scale  ' + node_name)
            Report_file.add_line('Order has been submitted for vnf scale  ' + node_name)
        else:
            log.error('Error while Order submission for vnf scale  ' + node_name + 'check logs for details')
            assert False

    except Exception as e:

        log.error('Error scale vnf type  ' + str(e))
        Report_file.add_line('Error scale vnf type ' + str(e))
        assert False