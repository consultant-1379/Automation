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
Created on jul 17, 2020

@author: zsyapra
'''
import queue
import time
import threading
import json
import concurrent.futures
from tabulate import tabulate
from com_ericsson_do_auto_integration_model.Ecm_PI import Ecm_PI
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Json_file_handler import Json_file_handler
from com_ericsson_do_auto_integration_utilities.MYSQL_DB import (get_PSQL_connection,
                                                                 get_table_data_from_PSQL_table_for_ecm_package_deletion)
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.SIT_files_update import (update_cnf_create_package_file,
                                                                         update_cnf_instanatiate_file,
                                                                         update_ns_cnf_remove,
                                                                         update_ns_cnf_add, update_ns_cnf_scale)

from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import (delete_node_vnf_package,
                                                                           delete_cnf_nsd_packages,
                                                                           get_ecm_package_list)
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import (
    upload_nsd_package,
    create_nsd_package,
    update_cnf_ns_ecm, scale_cnf_ns_ecm,
    get_cnf_vapp_mgt_id, create_ns_ecm,
    instantiate_ns_ecm)
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import get_package_upload_status

log = Logger.get_logger('CNF_NS_DEPLOYMENT.py')
lock = threading.RLock()
report_table_data = []


def print_cnf_package_report():
    try:
        lock.acquire()
        log.info('Package report for all cnf packages ')
        Report_file.add_line('Package report for all cnf packages')
        log.info(tabulate(report_table_data, headers=["PACKAGE NAME", "UPLOAD STATUS"], tablefmt='grid',
                          showindex="always"))
        Report_file.add_line(
            tabulate(report_table_data, headers=["PACKAGE NAME", "UPLOAD STATUS"], tablefmt='grid',
                     showindex="always"))

        for data in report_table_data:
            if 'UPLOAD FAILED' in data:
                log.error('Failure in package upload , please check the above table for more details')
                Report_file.add_line(
                    'Failure in package upload of minimum one node , please check the above table for more details')
                assert False
    except Exception as e:
        log.error('Error package upload' + str(e))
        Report_file.add_line('Error package upload' + str(e))
        assert False
    finally:
        lock.release()


def add_report_data_in_cnf_package_report(package_name, package_status):
    try:
        for data in report_table_data:
            if package_name in data:
                return

        report_data = [package_name, package_status]
        report_table_data.append(report_data)

    except Exception as e:
        log.info('Error adding report data in report table :' + e)


def upload_cnf_package(connection, token, vnf_instance_id, core_vm_hostname, cnf_package_name, pkg_dir_path,
                       idlist, exception_queue, success_queue):
    try:
        thread_name = threading.current_thread().name
        log.info("%s: Start to upload CNF package: %s", thread_name, cnf_package_name)
        Report_file.add_line('Start to upload CNF package' + str(cnf_package_name))
        cd_cmd = 'cd ' + pkg_dir_path
        curl_command = '''curl --insecure -i --location --request PUT "https://{}/ecm_service/SOL005/vnfpkgm/v1/vnf_packages/{}/package_content" --header 'Content-Type: application/zip' --header 'AuthToken:{}' -T "{}"'''.format(
            core_vm_hostname, vnf_instance_id, token, cnf_package_name)
        command = cd_cmd + ';' + curl_command
        Report_file.add_line('Command : ' + command)
        log.info(" Package " + str(cnf_package_name) + " Upload in progress, please wait....")
        log.info("%s: Executing command: %s", thread_name, command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        log.info("%s: Received output from command: %s", thread_name, command_output)

        Report_file.add_line('command output : ' + command_output)
        output = command_output
        global report_table_data
        if '100 Continue' in output:
            time_out = 3600
            wait_time = 90
            status = get_package_upload_status(connection, token, core_vm_hostname, vnf_instance_id, time_out,
                                               wait_time)

            if status == 'UPLOADED':
                log.info('Package ' + str(cnf_package_name) + ' uploaded successfully. ')
                Report_file.add_line('Package ' + str(cnf_package_name) + ' uploaded successfully. ')
                add_report_data_in_cnf_package_report(cnf_package_name, 'UPLOADED')
                success_queue.put(vnf_instance_id)
            else:
                log.info('Package ' + str(cnf_package_name) + ' upload failed. ')
                Report_file.add_line('Package ' + str(cnf_package_name) + ' upload failed. ')
                add_report_data_in_cnf_package_report(cnf_package_name, 'UPLOAD FAILED')
            log.info("Thread %s finished.", threading.current_thread().name)
        else:
            Report_file.add_line('Error in Upload CNF package')
            assert False
    except Exception as e:
        log.error('Error while Uploading CNF package ' + cnf_package_name + ' ' + str(e))
        Report_file.add_line('Error while uploading CNf package ' + cnf_package_name + ' ' + str(e))

        for i in idlist:
            log.info("Error while Uploading the package. Hence deleting the package ")
            Report_file.add_line("Error while Uploading the package. Hence deleting the package ")
            delete_cnf_nsd_packages(i, "TOSCA CNFD")

        exception_queue.put(e)


def fetch_package_details(packages):
    """
    Argument:
       packages = List of package names in ECM
       Example: ['spider-app-multi-a-1.0.2', 'spider-app-multi-b-1.0.2']
    """
    conn = None
    try:
        is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)

        if is_cloudnative:
            table_data = get_ecm_package_list()
        else:
            log.info('Start fetching package ids from RDB')
            Report_file.add_line('Start fetching package ids from RDB')
            ecm_gui_username = Ecm_core.get_ecm_gui_username(Ecm_core)
            rdb_vm_ip = Ecm_PI.get_rdb_vm_ip(Ecm_PI)
            db_password = Common_utilities.fetch_cmdb_password(Common_utilities)
            log.info('connecting with database to fetch the data')
            conn = get_PSQL_connection(rdb_vm_ip, 'ecmdb1', 'cmdb', db_password)
            table_data = get_table_data_from_PSQL_table_for_ecm_package_deletion(conn, 'id', 'package_format',
                                                                                 'is_enabled', 'name',
                                                                                 'cm_package', 'created_by',
                                                                                 ecm_gui_username)
        log.info('ECM package details - :%s', str(table_data))

        output = []
        if not table_data:
            for package_name in packages:
                log.info('Table data is empty. On- boarding package - %s', package_name)
                res = False, '', package_name
                output.append(res)
            return output
        else:
            for package_name in packages:
                val = True
                for record in table_data:
                    if package_name in record:
                        if 'Y' in record[2]:
                            log.info('Package already on-boarded. %s', package_name)
                            res = True, record[0], package_name
                            output.append(res)
                        else:
                            log.info('Package created with status as N. %s', package_name)
                            package_id = record[0]
                            res = False, package_id, package_name
                            output.append(res)
                        val = False
                if val:
                    log.info('Package not found in ECM package list/RDB. On- boarding package - %s', package_name)
                    res = False, '', package_name
                    output.append(res)
            return output
    except Exception as e:
        log.error('Error While fetching package details %s', str(e))
        Report_file.add_line('Error while fetching package details' + str(e))
        assert False
    finally:
        if conn:
            conn.close()


def onboard_packages_in_parallel(json_filename, pkgs_dir_path, packages_name_list, success_queue):
    ecm_connection = None
    exception_queue = queue.Queue()
    try:
        log.info('Starting to onboard packages in parallel.')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_hostname = Ecm_core.get_core_vm_hostname(Ecm_core)

        id_list = []
        package_count = 1
        pkg_count = 1

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for cnf_package_name in packages_name_list:
                pkg_name = cnf_package_name + ".csar"
                log.info('Onboarding package-%s', pkg_name)
                log.info('Making ecm connection')
                new_json_file = 'createpackage' + str(package_count) + '.json'
                package_count = package_count + 1
                with open(json_filename, "r") as jsonfile:
                    json_file_data = json.load(jsonfile)
                    Json_file_handler.update_json_file(Json_file_handler, new_json_file, json_file_data)
                update_cnf_create_package_file(new_json_file, cnf_package_name, pkg_name)
                log.info('Making ecm connection')
                ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
                log.info('Transferring %s file to blade host server', new_json_file)
                ServerConnection.put_file_sftp(ecm_connection,
                                               r'com_ericsson_do_auto_integration_files/' + new_json_file,
                                               SIT.get_base_folder(SIT) + new_json_file)

                time.sleep(2)
                token = Common_utilities.authToken(Common_utilities, ecm_connection, core_vm_hostname)
                command = '''curl --insecure "https://{}/ecm_service/SOL005/vnfpkgm/v1/vnf_packages" -H "Accept: application/json" -H "Content-Type: application/json" -H 'AuthToken: {}' --data @{}'''.format(
                    core_vm_hostname, token, new_json_file)
                output = Common_utilities.execute_curl_command(Common_utilities, ecm_connection, command)
                log.info("Curl command output: %s", str(output))

                if 'onboardingState' in output.keys():
                    if output['onboardingState'] == 'CREATED':
                        vnf_instance_id = output['id']
                        log.info('Create CNF package vnf_descriptors_id - %s', vnf_instance_id)
                        id_list.append(vnf_instance_id)
                        future = executor.submit(upload_cnf_package, ecm_connection, token, vnf_instance_id,
                                                 core_vm_hostname,
                                                 pkg_name, pkgs_dir_path, id_list, exception_queue, success_queue)
                        futures.append(future)
                        log.info(f"Started task: %s", future)
                        pkg_count = pkg_count + 1
                    else:
                        log.info('CNF package status %s', output['onboardingState'])
                else:
                    log.error('Error in Create CNF package %s', str(cnf_package_name))
                    assert False

            log.info('Thread Pool State: %s', futures)
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    log.info("Thread %s completed with result: %s", future, result)
                except Exception as e:
                    log.error("Thread raised an exception: %s", e)

        if not exception_queue.empty():
            raise exception_queue.get()
    except Exception as error:
        log.error('Error While creating CNF package %s', str(error))
        if ecm_connection:
            ecm_connection.close()
        assert False


def upload_tosca_cnf_package(pkgs_dir_path):
    ecm_connection = None
    try:
        log.info('Start to create CNF package')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        pkg_name_pattern = "*.csar"
        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        json_filename = r'com_ericsson_do_auto_integration_files/' + 'createpackage.json'
        command = 'find {} -name {}{}{}'.format(pkgs_dir_path, '"', pkg_name_pattern, '"')
        stdin, stdout, stderr = ecm_connection.exec_command(command)
        command_output = str(stdout.read())[2:-3:]
        output = command_output.split('\\n')
        ecm_connection.close()
        onboarded_pkgs, packages_name_list = [], []

        cnf_packages = [package.split(pkgs_dir_path)[1].split(".csar")[0] for package in output]
        package_details = fetch_package_details(cnf_packages)
        log.info('Package details from DB %s', str(package_details))
        for pkg_detail in package_details:
            is_enabled, package_id, pkg_name = pkg_detail
            if not is_enabled:
                if package_id != '':
                    log.info('Deleting package as its status is N in rdb - %s', pkg_name)
                    log.info('Deleting package id - %s', package_id)
                    delete_node_vnf_package(package_id)
                packages_name_list.append(pkg_name)
            else:
                log.info('Package already on-boarded as its status in rdb is Y - %s', pkg_name)
                onboarded_pkgs.append(package_id)

        if packages_name_list:
            success_queue = queue.Queue()
            onboard_packages_in_parallel(json_filename, pkgs_dir_path, packages_name_list, success_queue)
            successful_ids = list(success_queue.queue)
            if successful_ids:
                Common_utilities.create_artifact_prop_file(Common_utilities, successful_ids, 'TOSCA_CNF_INSTALL')
            print_cnf_package_report()
        if onboarded_pkgs:
            Common_utilities.create_artifact_prop_file(Common_utilities, onboarded_pkgs, 'TOSCA_CNF_INSTALL')

    except Exception as e:
        log.error('Error While creating CNF package %s', str(e))
        if ecm_connection:
            ecm_connection.close()
        assert False


def cnf_nsd_package_details():
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    pkgs_dir_path = sit_data._SIT__cnfconfigmapSoftwarePath
    package = 'ns-spider-app-ab-1.0.28.1.ab.zip'
    packageName = package.split('.zip')[0]
    filename = 'createNSDpackage.json'
    return pkgs_dir_path, package, packageName, filename


def create_cnfns_nsd_package():
    try:
        pkgs_dir_path, package, packageName, filename = cnf_nsd_package_details()
        create_nsd_package(packageName, filename)
    except Exception as e:
        log.error('Error While creating CNF NSD package ' + str(e))
        Report_file.add_line('Error while creating CNF NSD package ' + str(e))
        assert False


def upload_cnfns_nsd_package():
    try:
        pkgs_dir_path, package, packageName, filename = cnf_nsd_package_details()
        upload_nsd_package(pkgs_dir_path, package)
    except Exception as e:
        log.error('Error While uploading CNF NSD package ' + str(e))
        Report_file.add_line('Error while uploading CNF NSD package ' + str(e))
        assert False


def create_cnf_ns():
    create_ns_ecm("tosca-cnf", "CNF_NS_INSTANCE_ID")


def instantiate_tosca_cnf_ns():
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        file_name = 'instantiatecnf.json'
    else:
        file_name = 'instantiatecnf_classic.json'
    service_name = SIT.get_ecm_ns_name(SIT)
    update_cnf_instanatiate_file(file_name, service_name)
    instantiate_ns_ecm("tosca-cnf", file_name)


def remove_cnf_ns():
    """Update the NS with updateType=REMOVE_VNF to remove 1 instance of CNF-A."""

    ns_cnf_remove_file = 'ns_cnf_remove.json'
    ns_instance_id = SIT.get_cnf_ns_instance_id(SIT)
    cnf_vapp_mgt_id = get_cnf_vapp_mgt_id(ns_instance_id, 'cnfa1')
    if cnf_vapp_mgt_id:
        update_ns_cnf_remove(ns_cnf_remove_file, cnf_vapp_mgt_id)
        update_cnf_ns_ecm('cnf_remove', ns_cnf_remove_file)
    else:
        log.error('cnf with name cnfa2 not found in vapp list')
        assert False


def add_cnf_ns():
    """Update the NS with updateType=Add_VNF to add 1 instance of CNF-B."""

    ns_cnf_add_file = 'ns_cnf_add.json'
    cnf_vapp_instance_name = 'cnf-service-cnfb2'
    update_ns_cnf_add(ns_cnf_add_file, cnf_vapp_instance_name)
    update_cnf_ns_ecm('cnf_add', ns_cnf_add_file)


def scale_out_ns_cnf_vapp():
    """scale out on NS CNF vapp cnfa2"""
    file_name = "ecm_ns_cnf_scale.json"
    ns_instance_id = SIT.get_cnf_ns_instance_id(SIT)
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    instance_to_scale = 'cnfa2' if is_cloudnative else 'cnfa1'
    cnf_vapp_mgt_id = get_cnf_vapp_mgt_id(ns_instance_id, instance_to_scale)
    update_ns_cnf_scale(file_name, "SCALE_OUT", 3, cnf_vapp_mgt_id)
    scale_cnf_ns_ecm("SCALE_OUT", file_name)


def scale_in_ns_cnf_vapp():
    """scale in on NS CNF vapp cnfa2"""
    file_name = "ecm_ns_cnf_scale.json"
    ns_instance_id = SIT.get_cnf_ns_instance_id(SIT)
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    instance_to_scale = 'cnfa2' if is_cloudnative else 'cnfa1'
    cnf_vapp_mgt_id = get_cnf_vapp_mgt_id(ns_instance_id, instance_to_scale)
    update_ns_cnf_scale(file_name, "SCALE_IN", 2, cnf_vapp_mgt_id)
    scale_cnf_ns_ecm("SCALE_IN", file_name)
