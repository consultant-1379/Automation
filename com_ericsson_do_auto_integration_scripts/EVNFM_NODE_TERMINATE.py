import ast
import time
import evnfm

from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_model.EPIS import EPIS

log = Logger.get_logger('EVNFM_NODE_TERMINATE.py')


def terminate_evnfm_all():
    """This method is using the module from vnf-staging "evnfm"
    This will cleanup all the packages and resources from EVNFM"""

    log.info('Start to terminate EVNFM packages and resources ')
    Report_file.add_line('Start to terminate EVNFM packages and resources ')

    evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)
    evnfm_obj = evnfm.EVNFM(evnfm_hostname, evnfm_username, evnfm_password)

    additional_params = {
        "skipJobVerification": "true",
        "cleanUpResources": "true",
        "commandTimeout": "1200"
    }

    log.info('running the evnfm purge with additional params ' + str(additional_params))
    evnfm_obj.purge(additional_params_for_terminate=additional_params)

    log.info('Finished to terminate EVNFM packages and resources ')
    Report_file.add_line('Finished to terminate EVNFM packages and resources ')


def rollback_cnf_deployment(vnf_identifier_id):
    connection = None
    try:
        log.info(
            'Start clean up resources that are associated with a VNF instance due to a failed instantiate request')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        command = f'''curl -i --insecure -X POST https://{evnfm_hostname}/vnflcm/v1/vnf_instances/{vnf_identifier_id}/cleanup -H 'Accept: */*' -H 'Content-Type: application/json' -H 'cookie: JSESSIONID="{evnfm_token}"{"'"}'''

        log.info('Executing command: %s', command)
        output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('command output: %s', output)

        if '202 Accepted' in output:
            log.info('Clean up curl is successful  ')
        else:
            log.error('Error in cleanup curl output , please check logs for details')
            assert False

    except Exception as e:
        log.error('Error in cleanup curl output: %s', str(e))
        assert False
    finally:
        connection.close()


def terminate_cnf(node_name, file_name, software_dir, vnf_identifier_id):
    connection = None
    try:
        log.info('Start terminating %s', node_name)

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        path = '/var/tmp/{}/'.format(software_dir)

        curl = '''curl --insecure -i -X POST https://{}/vnflcm/v1/vnf_instances/{}/terminate -H 'Accept: */*' -H 'Content-Type: application/json' -H 'cookie: JSESSIONID={}' --data @{}'''.format(
            evnfm_hostname, vnf_identifier_id, evnfm_token, file_name)

        command = 'cd ' + path + ' ; ' + curl
        log.info('Executing command: %s', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('Terminating ccrc cnf command output: %s', command_output)

        if 'Accepted' in command_output:
            log.info('Termination started. Checking operationState')
        else:
            log.error('Termination command failed ')
            assert False

    except Exception as e:
        log.info('Error terminating CNF  ' + str(e))
        assert False
    finally:
        connection.close()


def cleanup_after_termination():
    nested_conn = None
    try:
        log.info('Start cleaning up after Termination')
        namespace = f'ccrc-{EPIS.get_cn_env_name(EPIS).lower()}'

        nested_conn = get_VMVNFM_host_connection(ccd1=True)

        command = f'kubectl delete pod --all -n {namespace}'
        log.info('Executing command: %s', command)
        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        log.info('command output %s', command_output)

        time.sleep(2)
        command = f'kubectl delete job --all -n {namespace}'
        log.info('Executing command: %s', command)
        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        log.info('command output %s', command_output)

        time.sleep(2)
        command = f'kubectl delete pvc --all -n {namespace}'
        log.info('Executing command: %s', command)
        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        log.info('command output %s', command_output)

        time.sleep(2)
        command = f'kubectl delete secret regcred -n {namespace}'
        log.info('Executing command: %s', command)
        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        log.info('command output %s', command_output)

        time.sleep(2)
        command = f'kubectl delete secret -l "com.ericsson.sec.tls/created-by=eric-sec-sip-tls" -n {namespace}'
        log.info('Executing command: %s', command)
        stdin, stdout, stderr = nested_conn.exec_command(command)
        command_output = str(stdout.read())
        log.info('command output %s', command_output)

        log.info('Finished cleaning up after Termination ')

    except Exception as e:
        log.info('Error cleaning up CCD ' + str(e))
        assert False

    finally:
        nested_conn.close()


def delete_vnf_identifier(vnf_identifier_id):
    connection = None
    try:
        log.info('Start deleting VNF Identifier')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        command = '''curl --insecure -i -X DELETE https://{}/vnflcm/v1/vnf_instances/{} -H 'Accept: */*' -H 'Content-Type: application/json' -H 'cookie: JSESSIONID={}{}'''.format(
            evnfm_hostname, vnf_identifier_id, evnfm_token, "'")

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        log.info('command output: %s', command_output)

        if '204 No Content' in command_output:
            log.info('VNF Identifier Deleted Successfully')

        else:
            log.error('VNF Identifier Deletion failed ')
            assert False

    except Exception as e:
        log.info('Error deleting VNF Identifier  ' + str(e))
        assert False
    finally:
        connection.close()


def delete_vnf_package(terminate_connection, evnfm_token, evnfm_hostname, package_id):
    try:
        log.info('Start deleting VNF package')

        command = '''curl --insecure -i -X DELETE https://{}/vnfm/onboarding/api/vnfpkgm/v1/vnf_packages/{} -H 'cookie: JSESSIONID={}{}'''.format(
            evnfm_hostname, package_id, evnfm_token, "'")

        log.info('Executing Command: %s', command)
        command_output = ExecuteCurlCommand.get_json_output(terminate_connection, command)
        log.info('command output: %s', command_output)

        if '204 No Content' in command_output:
            log.info('VNF package Deleted Successfully ' + package_id)
        else:
            log.error('VNF package Deletion failed ' + package_id)
            assert False

    except Exception as e:
        log.info('Error deleting VNF package  %s', str(e))
        assert False


def get_vnf_package(vnf_product_name):
    connection = None
    try:
        log.info('Getting VNF package')

        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        evnfm_hostname, evnfm_username, evnfm_password = Server_details.get_evnfm_details(Server_details)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        evnfm_token = Common_utilities.get_evnfm_token(Common_utilities, connection)

        command = '''curl --insecure -X GET https://{}/vnfm/onboarding/api/vnfpkgm/v1/vnf_packages/ -H 'Accept: */*' -H 'Content-Type: application/json' -H 'cookie: JSESSIONID="{}"{}'''.format(
            evnfm_hostname, evnfm_token, "'")

        log.info('Executing Command: %s', command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info('command output: %s', command_output)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)
        log.info('command output: %s', str(output))

        if len(output) > 0:
            for item_dict in output:
                package_id = item_dict['id']
                product_name = item_dict['vnfProductName']

                if vnf_product_name in item_dict['vnfProductName'] or vnf_product_name == 'ALL':
                    log.info('Deleting package id- ' + package_id)
                    delete_vnf_package(connection, evnfm_token, evnfm_hostname, package_id)
                else:
                    log.info(' No packages listed as per the input provided by user ')
        else:
            log.info(' No packages present on EVNFM')

    except Exception as e:
        log.info('Error getting VNF package  %s', str(e))
        assert False

    finally:
        connection.close()


def delete_secret():
    director_connection = None
    try:
        log.info('Deleting secret of CNF NS in EVNFM')
        vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)
        director_connection = get_VMVNFM_host_connection()

        command = 'kubectl delete secret -n ' + vm_vnfm_namespace + ' eric-eo-evnfm-nfvo'
        log.info('Executing Command: %s', command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info('Command output: %s', command_output)

        command = 'kubectl delete configmap -n ' + vm_vnfm_namespace + ' eric-eo-evnfm-nfvo-config'
        log.info('Executing Command: %s', command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info('Command output: %s', command_output)

    except Exception as e:
        log.info('Error while deleting secret in EVNFM  ' + str(e))
        assert False
    finally:
        director_connection.close()


def CCD_namespace_delete():
    """
     This method is used to delete namespaces provided via jenkins input.
     We have vnf_type attribute , that is used to take inputs from jenkins job .it can be any data according to job
     dont get confuse with vnf type , here we are using it for namespaces from jenkins job
     get_is_ccd is boolean value from DIT , according to which connection will be establish with director ip.
    """
    nested_conn = None
    try:
        log.info('Start deleting the namesapces from ccd director server')

        ccd = SIT.get_is_ccd(SIT)
        nested_conn = get_VMVNFM_host_connection(ccd)

        # getting all the available Namespaces from cluster
        command = "kubectl get ns --no-headers | awk '{print $1}'"
        stdin, stdout, stderr = nested_conn.exec_command(command)
        handle_stderr(stderr, log)

        cluster_ns_list = stdout.read().decode("utf-8").split()
        log.info('list of namespaces available on cluster %s', str(cluster_ns_list))

        ccd_namespace = SIT.get_vnf_type(SIT)
        log.info('namespaces to be deleted from user input:: %s ', ccd_namespace)

        input_ns_list = list(ccd_namespace.split(","))

        for ns in input_ns_list:
            for namespace in cluster_ns_list:
                if ns in namespace:
                    log.info('Deleting namespace: %s', namespace)
                    command = f'kubectl delete namespace {namespace}'
                    log.info('Executing command: %s', command)
                    stdin, stdout, stderr = nested_conn.exec_command(command)
                    command_error = str(stderr.read())
                    command_output = str(stdout.read())
                    log.info('stdout: %s', command_output)

                    if 'deleted' in command_output:
                        log.info('Namespace %s deleted successfully', namespace)

                    elif 'not found' in command_output or 'not found' in command_error:
                        log.warning('Namespace %s not found', namespace)

                    else:
                        log.error('Error while deleting the namespace %s. Command output: %s', namespace,
                                  command_output)
                        assert False
        log.info('Successfully deleted the namespaces provided by user found on cluster.')

    except Exception as e:
        log.info('Error deleting the namespace from ccd director server %s', str(e))
        assert False

    finally:
        nested_conn.close()
