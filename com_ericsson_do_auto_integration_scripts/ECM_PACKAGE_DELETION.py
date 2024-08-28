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
# pylint: disable=C0301,C0103,C0116,W0703,

'''
Created on Mar 18, 2020

@author: eiaavij
'''
import ast
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import get_package_status
from com_ericsson_do_auto_integration_utilities.MYSQL_DB import (
    get_PSQL_connection,
    get_table_data_from_PSQL_table_for_ecm_package_deletion)
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_model.Ecm_PI import Ecm_PI
from com_ericsson_do_auto_integration_model.EPIS import EPIS

log = Logger.get_logger('ECM_PACKAGE_DELETION.py')


def disable_node_package(vnf_package_id):
    try:
        log.info('Start Package Disable for package id %s', vnf_package_id)
        Report_file.add_line('Start Package Disable for package id ' + vnf_package_id)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        ServerConnection.put_file_sftp(connection,
                                       r'com_ericsson_do_auto_integration_files/empty_json.json',
                                       SIT.get_base_folder(SIT) + 'empty_json.json')
        command = '''curl --insecure "https://{}/ecm_service/vnfpackages/{}/disable" -H "Content-Type: application/json" -H "Accept: application/json" -H "AuthToken: {}" --data @empty_json.json'''.format(
            core_vm_hostname, vnf_package_id, token)

        Report_file.add_line('Curl command to disable package id ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ast.literal_eval(command_output[2:-1:1])
        request_status = output['status']['reqStatus']

        if 'SUCCESS' in request_status:
            log.info('Package Disabled successfully')
            Report_file.add_line('Package Disabled successfully')

        elif 'ERROR' in request_status:
            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for package disable: %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for package disable')
            assert False

    except Exception as error:
        log.info('Error Package Disable: %s', str(error))
        Report_file.add_line('Error Package Disable ' + str(error))
        assert False

    finally:
        connection.close()


def delete_node_vnf_package(vnf_package_id, onboard_failed=False):
    try:

        log.info('Start deleting tosca VNF package with id %s', vnf_package_id)
        Report_file.add_line('Start deleting tosca VNF package with id ' + vnf_package_id)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        command = '''curl --insecure "https://{}/ecm_service/vnfpackages/{}" -X DELETE  -H "Accept: application/json" -H "AuthToken: {}"'''.format(
            core_vm_hostname, vnf_package_id, token)

        Report_file.add_line('Curl command to delete package id ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ast.literal_eval(command_output[2:-1:1])
        request_status = output['status']['reqStatus']

        if 'SUCCESS' in request_status:
            if onboard_failed:
                log.info('Package deleted successfully')
                Report_file.add_line('Package deleted successfully ')
            else:
                try:
                    order_id = output['data']['order']['id']
                    order_status, order_output = Common_utilities.orderReqStatus(Common_utilities, connection,
                                                                                 token,
                                                                                 core_vm_hostname, order_id,
                                                                                 10)
                    if order_status:
                        log.info('Package deleted successfully with order id: %s', order_id)
                        Report_file.add_line('Package deleted successfully with order id  :' + order_id)
                    else:
                        log.info(order_output)
                        log.info('Order Status is failed with message mentioned above %s', order_id)
                        assert False
                except:
                    log.info('This package failed in onboarding , Package deleted successfully')

        elif 'ERROR' in request_status:
            command_error = output['status']['msgs'][0]['msgText']
            log.error('Error executing curl command for package delete %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for package delete')
            assert False

        log.info('Finished deleting tosca VNF package with id %s', vnf_package_id)
        Report_file.add_line('Finished deleting tosca VNF package with id ' + vnf_package_id)

    except Exception as error:
        log.info('Error deleting tosca VNF package %s', str(error))
        Report_file.add_line('Error deleting tosca VNF package ' + str(error))
        assert False

    finally:
        connection.close()


def delete_tosca_vnf_package(vnf_package_id, onboard_failed=False):
    log.info('Start disable and deleting tosca VNF package with id %s', vnf_package_id)
    Report_file.add_line('Start disable and deleting tosca VNF package with id ' + vnf_package_id)
    ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
    core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

    connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
    token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
    _, operational_state = get_package_status(connection, token, core_vm_hostname,
                                              vnf_package_id)
    connection.close()

    if 'ENABLED' in operational_state:
        disable_node_package(vnf_package_id)

    delete_node_vnf_package(vnf_package_id, onboard_failed)


def terminate_ecm_package(record):
    log.info('terminating starts now..')
    package_types_list = []
    if record[1] in ('TOSCA CNF', 'ETSI TOSCA NSD', 'ETSI TOSCA CNF'):
        package_types_list.append(record)
    else:
        if record[1] in ('EXTERNAL_FORMAT', 'ETSI TOSCA VNF'):
            if record[2] == 'Y':
                disable_node_package(record[0])
        delete_node_vnf_package(record[0])

    for pkg_type_details in package_types_list:
        delete_cnf_nsd_packages(pkg_type_details[0], pkg_type_details[1])


def start_terminating_ECM_packages():
    try:
        log.info('Start fetching package ids from RDB')
        Report_file.add_line('Start fetching package ids from RDB')
        ecm_gui_username = Ecm_core.get_ecm_gui_username(Ecm_core)
        vnf_type = SIT.get_vnf_type(SIT)
        rdb_vm_ip = Ecm_PI.get_rdb_vm_ip(Ecm_PI)
        db_password = Common_utilities.fetch_cmdb_password(Common_utilities)
        log.info('connecting with database to fetch the data')
        conn = get_PSQL_connection(rdb_vm_ip, 'ecmdb1', 'cmdb', db_password)
        table_data = get_table_data_from_PSQL_table_for_ecm_package_deletion(conn, 'id', 'package_format',
                                                                             'is_enabled',
                                                                             'name',
                                                                             'cm_package', 'created_by',
                                                                             ecm_gui_username)
        package_names_list = list(vnf_type.split(","))
        log.info(package_names_list)

        if 'ALL' in package_names_list:
            for record in table_data:
                terminate_ecm_package(record)
        else:
            for package_name in package_names_list:
                log.info('package name: %s', str(package_name))
                for record in table_data:
                    if package_name in record[3]:
                        log.info("%s found in ECM database , going to terminate it", package_name)
                        terminate_ecm_package(record)

    except Exception as error:
        log.error('Error in terminating ECM Package  :%s', str(error))
        assert False


def start_terminating_ECM_packages_cn():
    try:
        log.info('Start fetching package ids eocm from postgres db')
        vnf_type = SIT.get_vnf_type(SIT)
        table_data = get_ecm_package_list()
        log.info('ECM package details - :%s', str(table_data))

        package_names_list = list(vnf_type.split(","))
        log.info(package_names_list)

        if 'ALL' in package_names_list:
            for record in table_data:
                terminate_ecm_package(record)
        else:
            for package_name in package_names_list:
                log.info('package name: %s', str(package_name))
                for record in table_data:
                    if package_name in record[3]:
                        log.info('%s found in ECM database , going to terminate it', package_name)
                        terminate_ecm_package(record)

    except Exception as e:
        log.error('Error in terminating ECM Package  %s', str(e))
        assert False


def get_ecm_package_list():
    """
    Returns package details uploaded in ECM.
    Example output:
    [('09ecc4b6-5510-4f0c-ab16-ba26c703a399', 'TOSCA CNF', 'Y', 'spider-app-multi-a-1.0.2.csar'),
     ('1cf5b5b0-e52f-4139-ad88-17ad973e2aaa', 'EXTERNAL_FORMAT', 'Y', 'vnflaf'),
     ('c05919b3-4851-40c0-9252-e349389ba8df', 'TOSCA CNF', 'N', 'spider-app-multi-b-1.0.2.csar'),
     ('91cb5b11-79c6-460c-9a4f-4f79fc79bb6b', 'ETSI TOSCA NSD', 'Y', 'ns-spider-app-a2-1.0.28')]
    """
    log.info("Start fetching package details from ECM")
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)
        command = (
            f"curl -X GET --insecure --header 'Content-Type: application/json' --header 'Accept: application/json'"
            f" --header 'AuthToken: {token}' 'https://{core_vm_hostname}/ecm_service/vnfpackages'")
        output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ExecuteCurlCommand.get_sliced_command_output(output)
        log.info("command output for vnf packages %s", output)
        vnf_package_out = ast.literal_eval(output)
        command = (f"curl -X GET --insecure --header 'Content-Type: application/json' --header "
                   f"'Accept: application/json' --header 'AuthToken: {token}' 'https://{core_vm_hostname}"
                   f"/ecm_service/SOL005/nsd/v1/ns_descriptors?$filter="
                   f"byCharacteristics%3D%27true%27%20%27and%27%20tenantName%3D%27ECM%27&$data=%7B%22ericssonNfvoData%22%3Atrue%7D'")
        output = ExecuteCurlCommand.get_json_output(connection, command)
        output = ExecuteCurlCommand.get_sliced_command_output(output)
        log.info("command output for nsd packages %s", output)
        ns_package_out = ast.literal_eval(output)

        package_list = []
        if vnf_package_out and vnf_package_out.get('data'):
            for elem in vnf_package_out['data']['vnfPackages']:
                packages = [elem['id'], elem['packageFormat']]
                packages.append("Y") if elem['isEnabled'] else packages.append("N")
                packages.append(elem['name'])
                package_list.append(tuple(packages))
        if ns_package_out:
            for elem in ns_package_out:
                packages = [elem['id'], elem['ericssonNfvoData']['packageFormat']]
                packages.append("Y") if elem['nsdOperationalState'] == "ENABLED" else packages.append("N")
                packages.append(elem['ericssonNfvoData']['packageName'])
                package_list.append(tuple(packages))
        log.info("Finished fetching package details from ECM: %s", str(package_list))
        return package_list
    except Exception as error:
        log.error("Failed to fetch package details from ECM: %s", str(error))
        assert False
    finally:
        if connection:
            connection.close()


def get_nsd_package_status(connection, token, core_vm_hostname, package_id):
    log.info('curl command of verification of uploading the package')
    command = '''curl -X GET --insecure --header 'Accept: application/json' --header 'AuthToken: {}' 'https://{}/ecm_service/vnfpackages/{}'''.format(
        token, core_vm_hostname, package_id + "'")
    Report_file.add_line('Curl command for verifying OnBoarding the package ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
    output = ast.literal_eval(command_out)
    request_status = output['status']['reqStatus']
    provisioning_status = ''
    operational_state = ''

    if 'SUCCESS' in request_status:
        provisioning_status = 'ENABLED'
        operational_state = 'ENABLED'
    elif 'ERROR' in request_status:
        command_error = output['status']['reqStatus']
        log.error('Error executing curl command for verification of OnBoard package %s', command_error)
        Report_file.add_line(command_error)
        Report_file.add_line('Error executing curl command for verification of OnBoard package')

    return provisioning_status, operational_state


def delete_cnf_nsd_packages(package_id, pkg_format):
    connection = None
    try:
        log.info('Start to delete %s', pkg_format)
        Report_file.add_line('Start to delete ' + pkg_format)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        if pkg_format == 'ETSI TOSCA NSD':
            _, operational_state = get_nsd_package_status(connection, token, core_vm_hostname,
                                                          package_id)
        else:
            _, operational_state = get_package_status(connection, token, core_vm_hostname,
                                                      package_id)

        if 'ENABLED' in operational_state:
            disable_node_package(package_id)

        if pkg_format in ('TOSCA CNF', 'TOSCA CNFD', 'ETSI TOSCA CNF'):
            command = '''curl --insecure -i  "https://{}/ecm_service/SOL005/vnfpkgm/v1/vnf_packages/{}" -X "DELETE" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
                core_vm_hostname, package_id, token)
        elif pkg_format == 'ETSI TOSCA NSD':
            command = '''curl --insecure -i  "https://{}/ecm_service/SOL005/nsd/v1/ns_descriptors/{}" -X "DELETE" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
                core_vm_hostname, package_id, token)
        else:
            command = '''curl --insecure -i "https://{}/ecm_service/SOL005/nslcm/v1/ns_instances/{}"  -X "DELETE" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
                core_vm_hostname, package_id, token)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        Report_file.add_line('Command : ' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('deleting command output : ' + command_output)

        if '204 No Content' in command_output:
            log.info('Identifier Deleted Successfully %s', pkg_format)
            Report_file.add_line(pkg_format + ' Identifier Deleted Successfully')
        else:
            log.error('%s Identifier Deletion failed', pkg_format)
            Report_file.add_line(pkg_format + ' CNF Identifier Deletion failed ')
            assert False

    except Exception as error:
        log.error('Error deleting the %s: %s', pkg_format, str(error))
        Report_file.add_line('Error deleting the ' + pkg_format + ' ' + str(error))
        assert False

    finally:
        connection.close()


def remove_ecm_package_if_exists(package_name):
    """
    package_name : package name that needs to be check in ECM and cmdb
    Generic method to delete the package (Pre-check), that needs to checked before create or onboard
    """
    log.info('Start checking  package %s if exists', package_name)
    SIT.set_vnf_type(SIT, package_name)
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

    if is_cloudnative:
        start_terminating_ECM_packages_cn()
    else:
        start_terminating_ECM_packages()
