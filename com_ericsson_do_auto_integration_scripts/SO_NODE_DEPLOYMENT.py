# pylint: disable=C0302,C0103,C0301,C0412,E0602,W0621,C0411,R0915,E0602,W0611,W0212,W0703,R1714,W0613,R0914,W0105,R0913,E0401,W0705,W0612
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
import os
import zipfile
import shutil
import random
import re
from packaging import version
from com_ericsson_do_auto_integration_agat.AGAT_utilities import setup_so_api
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_model.EPIS import EPIS
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection, get_vmvnfm_pod_cmd
from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import check_so_network_service_state
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_runtime_env_file
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand
from com_ericsson_do_auto_integration_utilities.SO_file_update import (
    update_nsd_template_file, update_service_template, update_service_template_catalog,
    update_subsystem_file, update_day1Config_file, update_tenant_mapping_file, update_vnf_param_file)

log = Logger.get_logger('SO_NODE_DEPLOYMENT.py')

service_id = ''
so_host_name = ''
service_model_id = ''
ecm_template_name = ''
day1_template_name = ''


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file))


def fetch_so_version(node_name):
    connection = None
    try:

        log.info('Fetching SO Version for %s', node_name)
        Report_file.add_line(node_name + ' Fetching SO Version.')

        so_namespace = SIT.get_so_namespace(SIT)
        openstack_ip, username, password, openrc_filename = \
            Server_details.openstack_host_server_details(Server_details)
        directory_server_ip, directory_server_username = \
            Server_details.vm_vnfm_director_details(Server_details)

        connection = ServerConnection.get_connection(openstack_ip, username, password)

        if (
                node_name == 'Dummy'
                or node_name == 'Sol005_BGF'
                or node_name == 'Sol005_Dummy'
                or node_name == 'Sol005_EPG'
                or node_name == 'TEPG'
        ):
            log.info('In the Sol005_EPG case')

            ServerConnection.get_file_sftp(
                connection, r'/root/env06Files/eccd150-director-key', r'eccd150-director-key'
            )
            # we are reducing sleep time from 80 to 10 if any issue occurs try to make it 80 again
            time.sleep(10)
            vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
            if vm_vnfm_namespace == 'eo-deploy':
                log.info('Namespace used is: %s', vm_vnfm_namespace)
                # file_path = 'ccd-c16c028.director.pem'
                file_path = "eccd-2-3.pem"
                log.info('Using pem file: %s', file_path)
            else:
                file_path = 'eccd150-director-key'
                log.info('Using pem file: %s', file_path)

        elif node_name == 'subsystem':
            log.info('In the subsystem case')
            # This case is particular to other team not used in EO Staging.
            file_path = 'eccd-keypair_ALL.pem'
            ServerConnection.get_file_sftp(connection, f'/root/env06Files/{file_path}', file_path)

            time.sleep(10)
            log.info('Using pem file: %s', file_path)

        else:
            log.info('In the else case')
            vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
            if vm_vnfm_namespace == 'eo-deploy':
                log.info('Namespace used is: %s', vm_vnfm_namespace)
                # file_path = 'ccd-c16c028.director.pem'
                file_path = "eccd-2-3.pem"
                log.info('Using pem file: %s', file_path)
            else:
                file_path = 'eccd150-director-key'
                log.info('Using pem file: %s', file_path)

        nested_conn = ServerConnection.get_nested_server_connection(
            connection, openstack_ip, directory_server_ip, directory_server_username, file_path
        )
        time.sleep(2)

        eo_version = fetch_eo_version()
        if eo_version and eo_version < version.parse("1.42.0-153"):
            command = (f'kubectl describe pod -l app=eric-eo-orchestration-gui --namespace {so_namespace} | '

                       'awk /SO_VERSION/')

            log.info('command to fetch out SO version %s', command)
            stdin, stdout, stderr = nested_conn.exec_command(command)
            so_version = stdout.read().decode("utf-8").split()[1]
        else:
            command = ("kubectl get configmap eric-eo-so-orchestration-gui-env-configmap -o"
                       f"jsonpath='{{.data.SO_VERSION}}' -n {so_namespace}")
            log.info('command to fetch out SO version %s', command)
            stdin, stdout, stderr = nested_conn.exec_command(command)
            so_version = stdout.read().decode("utf-8")
        log.info('so version is: %s', so_version)

        time.sleep(2)
        nested_conn.close()
        if isinstance(version.parse(so_version), version.Version):
            if so_version == '0.0.0':
                so_version = '2.11.0-118'
            return version.parse(so_version)
        else:
            log.error('Invalid SO version: %s', so_version)
            assert False
    except Exception as error:
        log.error('Error fetching SO Version %s', str(error))
        Report_file.add_line('Error fetching SO Version ' + str(error))
        assert False

    finally:
        connection.close()


def fetch_eo_version():
    try:
        log.info('Start fetching EO VERSION')
        director_connection = get_VMVNFM_host_connection()
        namespace = SIT.get_so_namespace(SIT)
        command = 'helm ls -A | grep -i ' + "'" + 'eric-eo-' + namespace + "'"
        log.info('Executing command: ' + command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = stdout.read().decode("utf-8")
        log.info('command output :' + command_output)
        if command_output:
            eo_version = command_output.split()[8].split("eric-eo-")[1]
        else:
            return None
        if isinstance(version.parse(eo_version), version.Version):
            log.info("EO version is: %s", eo_version)
            return version.parse(eo_version)
        else:
            log.error('Invalid EO version: %s', eo_version)
            assert False
    except Exception as error:
        log.error('Failed to fetch EO version: %s', str(error))
        assert False


def fetch_nsd_package(software_path, nsd_package, service_template, so_version):
    connection = None
    try:
        log.info('Start fetching nsd package from ECM')
        Report_file.add_line('Start fetching nsd package from ECM')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        ServerConnection.get_file_sftp(
            connection,
            software_path + '/' + nsd_package,
            r'com_ericsson_do_auto_integration_files/' + nsd_package,
        )
        log.info('fetching service template from ECM')
        ServerConnection.get_file_sftp(
            connection,
            software_path + '/' + service_template,
            r'com_ericsson_do_auto_integration_files/' + service_template,
        )
        log.info('END fetching nsd package from ECM')
        Report_file.add_line('END fetching nsd package from ECM')

        if so_version >= version.parse('2.0.0-70'):
            # Transferring NSD package directly to root in this version of SO
            ServerConnection.put_file_sftp(
                connection, r'com_ericsson_do_auto_integration_files/' + nsd_package,
                            SIT.get_base_folder(SIT) + nsd_package
            )

    except Exception as e:
        log.error('Error fetching nsd package from ECM %s', str(e))
        Report_file.add_line('Error fetching nsd package from ECM ' + str(e))
        assert False

    finally:
        connection.close()


def update_NSD_template(nsd_package, unzipped_nsd_package, zipped_nsd_package, node_name, so_version):
    connection = None
    try:
        log.info('%s start updating NSD template', node_name)
        Report_file.add_line(node_name + ' updating NSD template begins...')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

        log.info('Unzipping the package %s', nsd_package)
        Report_file.add_line('Unzipping the package ' + nsd_package)
        zipfilePath = r'com_ericsson_do_auto_integration_files/' + nsd_package
        zip = zipfile.ZipFile(zipfilePath)
        zip.extractall(r'com_ericsson_do_auto_integration_files/' + unzipped_nsd_package)

        file_path = (
                r'com_ericsson_do_auto_integration_files/' + unzipped_nsd_package + '/Definitions/ns1.yaml'
        )
        update_nsd_template_file(file_path, node_name, so_version)

        zip_name = r'com_ericsson_do_auto_integration_files/' + unzipped_nsd_package
        directory_name = r'com_ericsson_do_auto_integration_files/' + unzipped_nsd_package

        shutil.make_archive(zip_name, 'zip', directory_name)

        log.info('rename the package %s', zipped_nsd_package)
        Report_file.add_line('rename the package ' + zipped_nsd_package)
        shutil.move(
            r'com_ericsson_do_auto_integration_files/' + zipped_nsd_package,
            r'com_ericsson_do_auto_integration_files/' + nsd_package,
        )

        log.info('delete the old package folder %s', unzipped_nsd_package)
        Report_file.add_line('rename the old package folder ' + unzipped_nsd_package)
        shutil.rmtree(r'com_ericsson_do_auto_integration_files/' + unzipped_nsd_package)

        log.info('Move updated nsd package to ECM server %s', ecm_server_ip)
        Report_file.add_line('Move updated nsd package to ECM server ' + ecm_server_ip)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        ServerConnection.put_file_sftp(
            connection, r'com_ericsson_do_auto_integration_files/' + nsd_package, SIT.get_base_folder(SIT) + nsd_package
        )

        log.info('End updating NSD template')
        Report_file.add_line('updating NSD template ends...')

    except Exception as e:
        log.error('Error NSD template %s', str(e))
        Report_file.add_line('Error NSD template ' + str(e))
        assert False

    finally:
        connection.close()


def onboard_NSD_Template(nsd_package, file_name, node_name, so_version):
    connection = None
    try:
        log.info('start onboarding NSD template')
        Report_file.add_line('onboarding NSD template begins...')

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        core_vm_ip = ecm_host_data._Ecm_core__CORE_VM_IP
        subsystem_name = sit_data._SIT__subsystem_name
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        token = Common_utilities.authToken(Common_utilities, connection, core_vm_hostname)

        log.info('Onboarding the NSD template using the token for authentication ')

        Report_file.add_line('Onboarding NSD Template using the token for authentication ')

        file_checksum = Common_utilities.crc(
            Common_utilities, r'com_ericsson_do_auto_integration_files/' + nsd_package
        )

        tenant_name = sit_data._SIT__tenantName
        auto_nsd_package = Common_utilities.get_name_with_timestamp(
            Common_utilities, 'Auto_nsd_package_' + node_name
        )
        data = (
                '"{\\"tenantName\\":\\"'
                + tenant_name
                + '\\",\\"package\\":{\\"nsdName\\":\\"'
                + auto_nsd_package
                + '\\",\\"nsdVersion\\":\\"1.0\\",\\"fileName\\":\\"'
                + nsd_package
                + '\\",\\"isPublic\\":true,\\"nsdDesigner\\":\\"Ericsson\\",\\"fileChecksum\\":\\"'
                + file_checksum
                + '\\",\\"chunkSize\\":\\"$(wc -c < '
                + nsd_package
                + ')\\",\\"chunkData\\":\\"$(base64 '
                + nsd_package
                + ')\\" }}"'
        )

        command = f'cd {SIT.get_base_folder(SIT)}; echo {data} > file_nsd_input.base64.req.body'
        log.info('command to create file_nsd_input.base64.req.body file %s', command)
        connection.exec_command(command)
        command = f'cd {SIT.get_base_folder(SIT)}; wc -c < {nsd_package}'
        stdin, stdout, stderr = connection.exec_command(command)
        command_output = str(stdout.read())
        range = command_output[2:-3:1]

        curl = (
                '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Accept: application/json' --header 'Content-Range: bytes 0-'''
                + str(int(range) - 1)
                + '/'
                + range
                + '''{} --header 'AuthToken: {}' --data @file_nsd_input.base64.req.body  'https://{}/ecm_service/nsd/v1/ns_descriptors{}'''.format(
            "'", token, core_vm_hostname, "'"
        )
        )
        command = curl
        log.info(command)
        Report_file.add_line('command :' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            nsd_id = output['data']['package']['nsdId']
            log.info(node_name + ' NSD id is ' + nsd_id)
            Report_file.add_line(node_name + ' NSD id  is ' + nsd_id)
            sit_data._SIT__nsd_id = nsd_id

        elif 'ERROR' in requestStatus:

            command_error = output['status']['msgs'][0]['msgText']

            log.error('Error executing curl command for onboarding NSD template %s', command_error)
            Report_file.add_line(command_error)
            Report_file.add_line('Error executing curl command for onboarding NSD template')
            connection.close()
            exit(-1)

        if so_version <= version.parse('1.2.2083'):

            update_service_template(file_name, nsd_id, node_name)

        else:
            update_service_template_catalog(
                file_name,
                nsd_id,
                node_name,
                day1_template_name,
                ecm_template_name,
                so_version,
                subsystem_name,
                tenant_name,
            )

        connection.close()
        log.info('onboarding NSD template and update of ServiceTemplate with nsdId ends')
        Report_file.add_line('onboarding NSD template and update of ServiceTemplate with nsdId ends')

    except Exception as e:
        log.error('Error onboarding NSD template  %s', str(e))
        Report_file.add_line('Error onboarding NSD template  ' + str(e))
        assert False

    finally:
        connection.close()


def so_files_transfer(software_path, node_name, package_name, so_version):
    connection = None
    try:
        openstack_ip, username, password, openrc_filename = \
            Server_details.openstack_host_server_details(Server_details)
        so_deployment_type = SIT.get_so_deployment_type(SIT)
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        so_host_name = SIT.get_so_host_name(SIT)
        directory_server_ip, directory_server_username = \
            Server_details.vm_vnfm_director_details(Server_details)
        so_version = fetch_so_version(node_name)

        if so_version <= version.parse('1.2.2083'):
            log.info('SO version is old , Start to copy the so-artifacts using script')
            connection = ServerConnection.get_connection(openstack_ip, username, password)
            ServerConnection.get_file_sftp(
                connection, r'/root/env06Files/eccd150-director-key', r'eccd150-director-key')

            # we are reducing sleep time from 80 to 10 if any issue occurs try to make it 80 again
            time.sleep(10)
            connection.close()
            file_path = 'eccd150-director-key'
            # so_artifacts_path = '/var/tmp/deployEPG2.4/'
            source_filepath = software_path + "/" + "so-artifacts/"
            destination_filepath = '/root'

            log.info('Copying the artifacts from host blade to gateway server: %s', openstack_ip)
            day1_file_path = software_path + '/so-artifacts/' + 'day1Config' + node_name + '.xml'
            day1_file_name = 'day1Config' + node_name + '.xml'
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            try:
                ServerConnection.get_file_sftp(
                    connection, day1_file_path, r'com_ericsson_do_auto_integration_files/' + day1_file_name)

            except FileNotFoundError:
                log.error('File Not Found Error : Wrong file or file path : %s', day1_file_path)
                assert False

            update_day1Config_file(day1_file_name, package_name, node_name)
            ServerConnection.put_file_sftp(
                connection, r'com_ericsson_do_auto_integration_files/' + day1_file_name, day1_file_path)
            filepath = '/' + ecm_username + '/'
            ServerConnection.transfer_folder_between_remote_servers(
                connection, openstack_ip, username, password, source_filepath,
                destination_filepath, filepath, "put")

            connection.close()
            log.info('Copying the so-artifacts from host blade to gateway server, %s', openstack_ip)
            connection = ServerConnection.get_connection(openstack_ip, username, password)
            log.info('Connected with the Gateway server %s', openstack_ip)
            command = 'scp -i env06Files/eccd150-director-key -r so-artifacts/ {}@{}:/home/eccd'.format(
                directory_server_username, directory_server_ip
            )
            stdin, stdout, stderr = connection.exec_command(command)
            log.info('Copied Artifacts from Gateway onto  directory node: %s', command)
            log.info(
                'Copied so-Artifacts from Gateway onto directory node: %s', directory_server_ip)
            log.info('Copying the artifacts to workflow pod ')
            nested_conn = ServerConnection.get_nested_server_connection(
                connection, openstack_ip, directory_server_ip, directory_server_username, file_path
            )
            time.sleep(10)
            command = 'chmod 777 /home/eccd/so-artifacts/transfer_so_files_' + node_name + '.sh '
            log.info('giving permission to transfer_so_files_%s.sh : %s', node_name, command)
            stdin, stdout, stderr = nested_conn.exec_command(command)
            time.sleep(5)
            command = 'cd  /home/eccd/so-artifacts/ ; ./transfer_so_files_' + node_name + '.sh '
            log.info('Copying the artifacts to workflow pod using command  :%s', command)
            stdin, stdout, stderr = nested_conn.exec_command(command)
            time.sleep(5)
            log.info('Copied the artifacts to workflow pod using command  :%s', str(stdout))
            log.info(stderr)
            nested_conn.close()
            connection.close()
        else:
            log.info('SO version is new , Onboarding of day1 and ecm template using catalog manager')
            if so_version >= version.parse('2.0.0-70'):
                if node_name != 'Sol005_EPG':
                    ecm_template_path = (
                            software_path + '/so-artifacts/' + 'EcmTemplate' + node_name + '_new.txt')
                    ecm_file_name = 'EcmTemplate' + node_name + '_new.txt'
                day1_file_path = software_path + '/so-artifacts/' + 'day1Config' + node_name + '_new.xml'
                day1_file_name = 'day1Config' + node_name + '_new.xml'
            else:
                if node_name != 'Sol005_EPG':
                    ecm_template_path = software_path + '/so-artifacts/' + 'EcmTemplate' + node_name + '.txt'
                    ecm_file_name = 'EcmTemplate' + node_name + '.txt'
                day1_file_path = software_path + '/so-artifacts/' + 'day1Config' + node_name + '.xml'
                day1_file_name = 'day1Config' + node_name + '.xml'
            if so_deployment_type == 'IPV6':
                log.info('SO Deployment type is IPV6, connecting with open stack ')
                connection = ServerConnection.get_connection(openstack_ip, username, password)
            else:
                connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            try:
                if node_name != 'Sol005_EPG':
                    ServerConnection.get_file_sftp(
                        connection, ecm_template_path,
                        r'com_ericsson_do_auto_integration_files/' + ecm_file_name)
                ServerConnection.get_file_sftp(
                    connection, day1_file_path, r'com_ericsson_do_auto_integration_files/' + day1_file_name)

            except FileNotFoundError as err:
                log.error('File Not Found Error : Wrong file or file path: %s', str(err))
                assert False

            if so_version >= version.parse('2.0.0-70'):
                log.info('No need to update day1 config file for this version of SO %s', str(so_version))
            else:
                update_day1Config_file(day1_file_name, package_name, node_name)

            if node_name != 'Sol005_EPG':
                ServerConnection.put_file_sftp(
                    connection,
                    r'com_ericsson_do_auto_integration_files/' + ecm_file_name,
                    SIT.get_base_folder(SIT) + ecm_file_name)
            ServerConnection.put_file_sftp(
                connection,
                r'com_ericsson_do_auto_integration_files/' + day1_file_name,
                SIT.get_base_folder(SIT) + day1_file_name)

            token_user = 'staging-user'
            token_password = 'Testing12345!!'
            token_tenant = 'staging-tenant'
            so_token = Common_utilities.generate_so_token(
                Common_utilities, connection, so_host_name, token_user, token_password, token_tenant)

            if node_name != 'Sol005_EPG':
                global ecm_template_name
                ecm_template_name = Common_utilities.get_name_with_timestamp(
                    Common_utilities, node_name + '_ecm_template')

                command = ExecuteCurlCommand.curl_onboard_so_template(
                    so_version, ecm_file_name, ecm_template_name, so_host_name, so_token, 'CONFIG_TEMPLATE')
                log.info('command : %s', command)
                command_output = ExecuteCurlCommand.get_json_output(connection, command)
                log.info('command output : %s', command_output)

            global day1_template_name
            day1_template_name = Common_utilities.get_name_with_timestamp(
                Common_utilities, node_name + '_day1_template'
            )
            SIT.set_day1_template_name(SIT, day1_template_name)
            command = ExecuteCurlCommand.curl_onboard_so_template(
                so_version, day1_file_name, day1_template_name, so_host_name, so_token,
                'CONFIG_TEMPLATE', '-i')
            log.info('command : %s', command)
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            log.info('command output : %s', command_output)
            log.info('Finished Onboarding of day1 and ecm template using catalog manager')
    except Exception as e:
        log.error('Error transfer SO files  %s', str(e))
        assert False
    finally:
        connection.close()


def verify_onboard_subsystem(connection, ecm_subsystem_name, mgtype, so_token):
    log.info('wait for 5 seconds to finish onboarding process')
    time.sleep(5)
    log.info('Start verification of onboarded subsystem %s', ecm_subsystem_name)
    Report_file.add_line('Start verification of onboarded subsystem ' + ecm_subsystem_name)

    curl = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/subsystem-manager/v1/subsystems'''.format(
        so_token, so_host_name
    )

    command = curl
    log.info(command)
    Report_file.add_line('command : ' + command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    output = ExecuteCurlCommand.get_sliced_command_output(command_output)

    data = ast.literal_eval(output)

    total_items = len(data)

    if total_items != 0:
        item_list = data
        for count in range(total_items):
            item_dict = item_list[count]
            if mgtype in item_dict['subsystemType'].values():
                name = item_dict['name']
                if ecm_subsystem_name == name:
                    return True

        return False

    else:
        return False


def start_onboard_subsystem(name, mgtype):
    log.info('start onboarding subsystem %s', name)
    Report_file.add_line('start onboarding subsystem ' + name)

    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    global so_host_name
    so_host_name = sit_data._SIT__so_host_name
    so_deployment_type = sit_data._SIT__so_deployment_type
    tenant_name = sit_data._SIT__tenantName
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    token_user = 'so-user'
    token_password = 'Ericsson123!'
    token_tenant = 'master'

    subsystem_name = name + '_' + str(random.randint(0, 999))

    if name == 'ECM' or name == 'SOL005_EOCM':
        sit_data._SIT__subsystem_name = subsystem_name
        update_runtime_env_file('SUBSYSTEM_NAME', subsystem_name)
    if so_deployment_type == 'IPV6':

        log.info('SO Deployment type is IPV6, connecting with open stack ')
        connection = ServerConnection.get_connection(openstack_ip, username, password)

    else:

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    so_token = Common_utilities.generate_so_token(
        Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
    )
    log.info('Onboarding subsystem using the token for authentication %s', name)
    Report_file.add_line('Onboarding subsystem using the token for authentication ' + name)

    if name == 'ECM':
        # file_name = 'ECM_subsystem_newParams.json'
        log.info('Adapter: eric-eo-ecm-adapter is deprecated. Please use supported adapter')
        assert False

    elif name == 'SOL005_EOCM':
        file_name = 'ECM_sol005_subsystem.json'

    else:
        file_name = 'new_subsystem_' + name + '.json'

    curl = ('curl -X POST --insecure --header "Content-Type: application/json" --header' +
            ' "Cookie: JSESSIONID={}" --data @'.format(so_token) + file_name +
            ' https://{}/subsystem-manager/v1/subsystems'.format(so_host_name))

    update_subsystem_file(file_name, subsystem_name, tenant_name)

    sftp = connection.open_sftp()
    if so_deployment_type == 'IPV6':
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, '/root/' + file_name)
    else:
        sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, SIT.get_base_folder(SIT) + file_name)

    log.info('curl command for Onboarding subsystem %s', subsystem_name)

    command = curl
    log.info(command)
    Report_file.add_line('command :' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    success = verify_onboard_subsystem(connection, subsystem_name, mgtype, so_token)

    if success:
        log.info('Finished onboarding subsystem with verification %s', subsystem_name)
        Report_file.add_line('Finished onboarding subsystem with verification ' + subsystem_name)

        if name == 'ECM' or name == 'SOL005_EOCM':

            log.info('Subsystem %s is going to do tenant mapping', name)
            Report_file.add_line('command output :' + command_output)

            output = ExecuteCurlCommand.get_sliced_command_output(command_output)
            data = ast.literal_eval(output)

            subsystem_id = data['id']
            connection_prop_id = data['connectionProperties'][0]['id']

            file_name = 'tenant_mapping.json'

            update_tenant_mapping_file(file_name, 'staging-tenant', subsystem_id, connection_prop_id)
            if so_deployment_type == 'IPV6':
                ServerConnection.put_file_sftp(
                    connection, r'com_ericsson_do_auto_integration_files/' + file_name, r'/root/' + file_name
                )
            else:
                ServerConnection.put_file_sftp(
                    connection, r'com_ericsson_do_auto_integration_files/' + file_name,
                                SIT.get_base_folder(SIT) + file_name
                )

            command = (
                    '''curl -X POST --insecure --header 'Content-Type: application/json' --header 'Cookie: JSESSIONID="{}"' --data @'''.format(
                        so_token
                    )
                    + file_name
                    + ''' https://{}/subsystem-manager/v1/tenant-mappings'''.format(so_host_name)
            )

            if so_deployment_type != 'IPV6':
                command = f'cd {SIT.get_base_folder(SIT)}; {command}'

            log.info('tenant mapping %s', command)
            Report_file.add_line('tenant mapping command :' + command)
            stdin, stdout, stderr = connection.exec_command(command)

            if stdout:

                command_output = str(stdout.read())
                Report_file.add_line('tenant mapping command output :' + command_output)
                connection.close()

            else:
                command_error = str(stderr.read())
                Report_file.add_line('tenant mapping failed command output :' + command_error)
                connection.close()
                assert False

    else:
        log.error(
            'subsystem onboarding failed , not found in subsystem list while verification %s', subsystem_name
        )
        Report_file.add_line(
            'subsystem onboarding failed , not found in subsystem list while verification ' + subsystem_name
        )
        connection.close()
        assert False


def onboard_subsytems():
    start_onboard_subsystem('ECM', 'NFVO')
    start_onboard_subsystem('ENM', 'DomainManager')
    start_onboard_subsystem('MULTI_ENM', 'DomainManager')
    start_onboard_subsystem('SOL005_EOCM', 'NFVO')


def check_entity_exists(entity_name, connection, command):
    log.info('Checking if the %s exists ', entity_name)
    Report_file.add_line('Checking if the ' + entity_name + 'exists ')
    log.info(command)
    Report_file.add_line('command : ' + command)
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    log.info('Received output before parsing: %s', command_output)

    output = ast.literal_eval(command_out)
    log.info(output)

    total_items = len(output)
    if total_items != 0:
        item_list = output
        return total_items, item_list
    else:
        return 0, []


def delete_subsystems(connection, total_items, item_list, so_host_name, so_token):
    log.info('Start deleting subsystems')
    Report_file.add_line('Start deleting subsystems')

    for count in range(total_items):
        item_dict = item_list[count]
        id = item_dict['id']

        command = '''curl -i -X DELETE --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/subsystem-manager/v1/subsystems/{}'''.format(
            so_token, so_host_name, id
        )

        log.info(command)
        Report_file.add_line('command :' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        Report_file.add_line('command output:' + command_output)

        if '204 No Content' in command_output:
            log.info('Finished deleting subsystems')
            Report_file.add_line('Finished deleting subsystems')

        else:
            log.error('Error while deleting the subsystem , please check output for more details')
            log.error('Command output %s', command_output)
            assert False


def check_new_entity_exists(entity_name, connection, command):
    log.info('Checking if the %s exists ', entity_name)
    Report_file.add_line('Checking if the ' + entity_name + 'exists ')
    log.info(command)
    Report_file.add_line('command : ' + command)

    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    output = ast.literal_eval(command_out)
    total_items = len(output)

    if total_items != 0:
        item_list = output
        return total_items, item_list
    else:
        return 0, []


def onboard_enm_ecm_subsystems(node_name):
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    global so_host_name
    so_deployment_type = sit_data._SIT__so_deployment_type
    so_host_name = sit_data._SIT__so_host_name
    token_user = 'so-user'
    token_password = 'Ericsson123!'
    token_tenant = 'master'

    if so_deployment_type == 'IPV6':

        log.info('SO Deployment type is IPV6, connecting with open stack ')
        connection = ServerConnection.get_connection(openstack_ip, username, password)

    else:

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    so_token = Common_utilities.generate_so_token(
        Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
    )

    command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/subsystem-manager/v1/subsystems'''.format(
        so_token, so_host_name
    )
    total_subs, subs_data = check_new_entity_exists('subsystems', connection, command)

    exist_sub_dict = {}

    for item in range(0, total_subs):
        item_dict = subs_data[item]
        name = item_dict['name']
        id = item_dict['id']
        if 'SOL005_EOCM' in name:
            exist_sub_dict['SOL005_EOCM'] = item_dict
        elif 'ECM' in name:
            exist_sub_dict['ECM'] = item_dict
        elif 'MULTI_ENM' in name:
            exist_sub_dict['MULTI_ENM'] = item_dict
        elif 'ENM' in name:
            exist_sub_dict['ENM'] = item_dict
        else:
            exist_sub_dict['OTHER'] = item_dict

    exists_key = exist_sub_dict.keys()

    if (
            node_name == 'Sol005_BGF'
            or node_name == 'TEPG'
            or node_name == 'Sol005_Dummy'
            or node_name == 'Sol005_EPG'
            or node_name == 'SOL005_CONFIGMAP'
            or node_name == 'SOL005_subsystem'
    ):
        if 'ECM' in exists_key:
            log.info('Subsystem with name %s already exists', exist_sub_dict["ECM"])
            dict = exist_sub_dict['ECM']
            item_list = [dict]
            delete_subsystems(connection, 1, item_list, so_host_name, so_token)
            log.info('waiting 10 seconds to complete deletion')
            time.sleep(10)

        if 'SOL005_EOCM' in exists_key:
            log.info('Updating Subsystem name %s as already exists', exist_sub_dict["SOL005_EOCM"])
            dict = exist_sub_dict['SOL005_EOCM']
            sol_ecm_subsystem_name = dict['name']
            sit_data._SIT__subsystem_name = sol_ecm_subsystem_name
            update_runtime_env_file('SUBSYSTEM_NAME', sol_ecm_subsystem_name)
        else:
            log.info('onboarding subsystem for SOL005_EOCM')
            start_onboard_subsystem('SOL005_EOCM', 'NFVO')

    else:
        if 'SOL005_EOCM' in exists_key:
            log.info('Subsystem with name %s already exists', exist_sub_dict["SOL005_EOCM"])
            dict = exist_sub_dict['SOL005_EOCM']
            item_list = [dict]
            delete_subsystems(connection, 1, item_list, so_host_name, so_token)
            log.info('waiting 10 seconds to complete deletion')
            time.sleep(10)

        if 'ECM' in exists_key:
            log.info('Updating Subsystem name %s as already exists', exist_sub_dict["ECM"])
            dict = exist_sub_dict['ECM']
            ecm_subsystem_name = dict['name']
            sit_data._SIT__subsystem_name = ecm_subsystem_name
            update_runtime_env_file('SUBSYSTEM_NAME', ecm_subsystem_name)

        else:
            log.info('onboarding subsystem for ECM')
            start_onboard_subsystem('ECM', 'NFVO')

    if 'MULTI_ENM' in exists_key:
        log.info('Subsystem with name %s already exists', exist_sub_dict["MULTI_ENM"])
    else:
        log.info('onboarding subsystem for MULTI_ENM')
        start_onboard_subsystem('MULTI_ENM', 'DomainManager')

    if 'ENM' in exists_key:
        log.info('Subsystem with name %s already exists', exist_sub_dict["ENM"])
    else:
        log.info('onboarding subsystem for ENM')
        start_onboard_subsystem('ENM', 'DomainManager')


def fetch_service_modelId_uds_so_template(node_name):
    connection = None
    try:
        log.info('fetching service model id from vf name for VNF %s', node_name)
        Report_file.add_line(f'fetching service model id from vf name for VNF {node_name}')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')

        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_deployment_type = sit_data._SIT__so_deployment_type
        so_host_name = sit_data._SIT__so_host_name
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password

        token_user = 'so-user'
        token_password = 'Ericsson123!'
        token_tenant = 'master'
        global service_model_id

        if so_deployment_type == 'IPV6':

            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        so_token = Common_utilities.generate_so_token(
            Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
        )

        vf_name = sit_data._SIT__uds_vf_name

        log.info('VF name is %s', vf_name)

        Report_file.add_line('VF name is ' + vf_name)

        command = f'''curl -X GET --insecure -H 'content-type: application/json' -H 'cookie: JSESSIONID={so_token};' https://{so_host_name}/catalog-manager/artifact/catalog-manager/v2/catalogs?filters=%7B%22name%22%3A%22{vf_name}%22%7D'''

        Report_file.add_line('command :' + command)
        timeout = 300
        log.info('Timeout for this process is 300 seconds')

        while timeout != 0:
            command_output = ExecuteCurlCommand.get_json_output(connection, command)
            command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
            Report_file.add_line('command output :' + command_output)
            output = ast.literal_eval(command_out)

            if not output:
                log.info('Service model Id is not yet created ')
                log.info('waiting 10 seconds to check again ...')
                timeout = timeout - 10
                time.sleep(10)
            else:
                output = output[0]
                if output['type'] == 'SERVICE_TEMPLATE':
                    if output['status'] == 'ACTIVE':
                        service_model_id = output['referenceId']
                        invariant_uuid = output['invariantUUID']

                        log.info('serviceModelId is %s', service_model_id)
                        log.info('invariantUUID is %s', invariant_uuid)
                        Report_file.add_line('invariantUUID is  is ' + invariant_uuid)
                        Report_file.add_line('serviceModelId  is ' + service_model_id)
                        log.info('Service model Id is %s verification successful ..', service_model_id)

                        sit_data._SIT__service_model_id = service_model_id
                        sit_data._SIT__invariant_uuid = invariant_uuid
                        break

                    else:
                        log.info('Service status is %s: ', output['status'])
                        log.info('Waiting 10 seconds to check again ...')
                        timeout = timeout - 5
                        time.sleep(5)

        if timeout <= 0:
            log.error(
                'timed out while fetching service model id, Service template not onboarded to SO, \
                            please check SO/UDS logs. '
            )
            Report_file.add_line(
                'timed out while fetching service model id, \
                                Service template not onboarded to SO, please check SO/UDS logs. '
            )
            assert False

    except Exception as e:
        log.error('Error Fetching service model id  %s', str(e))
        Report_file.add_line('Error Fetching service model id ' + str(e))
        assert False

    finally:
        connection.close()


def onboard_so_template(file_name, node_name, so_version, unique_filename_option=''):
    connection = None
    try:
        log.info('%s start onboarding SO Template', node_name)
        Report_file.add_line(node_name + ' Start Onboarding SO Template...')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
        ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
        ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
        so_deployment_type = sit_data._SIT__so_deployment_type
        openstack_ip = EPIS_data._EPIS__openstack_ip
        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        so_host_name = sit_data._SIT__so_host_name
        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        if so_deployment_type == 'IPV6':
            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)
            base_dir = '/root/'
        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
            base_dir = SIT.get_base_folder(SIT)
        ServerConnection.put_file_sftp(
            connection, r'com_ericsson_do_auto_integration_files/' + file_name, base_dir + file_name)

        so_token = Common_utilities.generate_so_token(
            Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
        )

        log.info('Onboarding the SO Template using the token for authentication ')

        Report_file.add_line('Onboarding SO template using the token for authentication ')

        if unique_filename_option == 'SOL-CNF-CONFIG-MAP':
            st_unique_name = 'ST_CNF_CONFIGMAP'
        else:
            st_unique_name = Common_utilities.get_name_with_timestamp(
                Common_utilities, node_name + '_service_template'
            )

        log.info('SO Template with unique name: %s', st_unique_name)
        Report_file.add_line('SO Template with unique name: ' + st_unique_name)

        curl = ExecuteCurlCommand.curl_onboard_so_template(
            so_version, file_name, st_unique_name, so_host_name, so_token, 'SERVICE_TEMPLATE'
        )

        command = curl
        log.info(command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command, base_folder=base_dir)

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)
        if not command_out:
            log.error('Failed to onboard SO Template')
            Report_file.add_line('Failed to onboard SO Template')
            assert False
        output = ast.literal_eval(command_out)
        if so_version >= version.parse('2.11.0-118'):
            if so_version < version.parse('2.11.0-551'):
                service_model_id = output['id']
                invariant_uuid = output['invariantUUID']
            else:
                if 'jobId' not in output.keys():
                    log.error('Failed to onboard SO Template')
                    Report_file.add_line('Failed to onboard SO Template')
                    assert False
                job_id = output['jobId']
                curl = (
                    f'curl -X GET --insecure -H "content-type: application/json" -H "cookie: JSESSIONID={so_token}"'
                    f' https://{so_host_name}/onboarding/v3/jobs/{job_id}'
                )
                log.info('command :%s', curl)

                timeout = 60

                while timeout >= 0:
                    job_response = ExecuteCurlCommand.get_json_output(connection, curl, base_folder=base_dir)
                    job_response_out = ExecuteCurlCommand.get_sliced_command_output(job_response)
                    if not job_response_out:
                        log.error('Error fetching job response')
                        Report_file.add_line(f'Error fetching job response')
                        assert False
                    job_output = ast.literal_eval(job_response_out)

                    if job_output['status'] == 'COMPLETED':
                        artifact_id = job_output['jobData']['artifactId']
                        curl = (
                            f'curl -X GET --insecure -H "content-type: application/json"'
                            f' -H "cookie: JSESSIONID={so_token}" '
                            f'https://{so_host_name}/catalog-manager/artifact/catalog-manager/v2/catalogs/{artifact_id}'
                        )

                        log.info('command :' + curl)
                        artf_response = ExecuteCurlCommand.get_json_output(connection, curl, base_folder=base_dir)
                        artf_response_out = ExecuteCurlCommand.get_sliced_command_output(artf_response)
                        artifact_output = ast.literal_eval(artf_response_out)
                        service_model_id = artifact_output['referenceId']
                        invariant_uuid = artifact_output['invariantUUID']
                        break
                    elif job_output['status'] == "FAILED":
                        log.error('Failed to onboard SO Template')
                        Report_file.add_line('Failed to onboard SO Template')
                        assert False
                    elif timeout <= 0:
                        log.error(
                            "onboarding service template response timed out, status is: %s",
                            job_output['status'],
                        )
                        Report_file.add_line(
                            'onboarding service template response timed out, status is: '
                            + job_output['status']
                        )
                        assert False
                    elif job_output['status'] == 'IN_PROGRESS':
                        time.sleep(4)
                        timeout = timeout - 4
            log.info('serviceModelId is %s', service_model_id)
            Report_file.add_line('serviceModelId  is ' + service_model_id)
            sit_data._SIT__service_model_id = service_model_id
            log.info('invariantUUID is %s', invariant_uuid)
            Report_file.add_line('invariantUUID is ' + invariant_uuid)
            sit_data._SIT__invariant_uuid = invariant_uuid
        else:
            service_model_id = output['id']
            log.info('serviceModelId is %s', service_model_id)
            Report_file.add_line('serviceModelId  is ' + service_model_id)
            sit_data._SIT__service_model_id = service_model_id

    except Exception as e:
        log.error('Error onboarding SO Template %s', str(e))
        Report_file.add_line('Error onboarding SO Template ' + str(e))
        assert False

    finally:
        connection.close()


def create_network_service(file, so_version):
    log.info('start creating network service ')
    Report_file.add_line('start creating network service  begins...')

    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password
    token_user = 'staging-user'
    token_password = 'Testing12345!!'
    token_tenant = 'staging-tenant'
    so_deployment_type = sit_data._SIT__so_deployment_type
    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password

    if so_deployment_type == 'IPV6':

        log.info('SO Deployment type is IPV6, connecting with open stack ')
        connection = ServerConnection.get_connection(openstack_ip, username, password)
        base_dir = '/root/'

    else:

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        base_dir = SIT.get_base_folder(SIT)

    so_token = Common_utilities.generate_so_token(
        Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
    )

    log.info('creating the network service using the token for authentication ')

    Report_file.add_line('creating the network service using the token for authentication  ')
    global service_id
    if so_version >= version.parse('2.11.0-118'):
        so_api = setup_so_api()
        service_order_id = so_api.service_order_client._create_service_order(file)
        Report_file.add_line('Service order Id Using AGAT libs - ' + service_order_id)
        json_output = so_api.service_order_mgmt.get_service_order_by_id(service_order_id).json()
        Report_file.add_line('create network service AGAT output - ' + str(json_output))
        service_id = service_order_id
        # service_id = json_output['serviceOrderItem'][0]['service']['id']
        # Report_file.add_line(Report_file, 'Service Id Using AGAT libs - ' + service_id)
        # curl = '''curl --insecure 'https://{}/service-order-mgmt/v1/serviceOrder' -H 'Cookie: JSESSIONID="{}"' -H 'Content-Type: application/json' -H 'Accept: application/json' -X POST --data @{}'''.format(so_host_name, so_token, file_name)
    else:
        ServerConnection.put_file_sftp(
            connection, r'com_ericsson_do_auto_integration_files/' + file, SIT.get_base_folder(SIT) + file
        )
        curl = '''curl --insecure 'https://{}/orchestration/v1/services' -H 'Cookie: JSESSIONID="{}"' -H 'Content-Type: application/json' -H 'Accept: application/json' -X POST --data @{}'''.format(
            so_host_name, so_token, file
        )
        command = curl
        log.info(command)
        Report_file.add_line('command :' + command)

        command_output = ExecuteCurlCommand.get_json_output(connection, command, base_folder=base_dir)

        Report_file.add_line('command output :' + command_output)

        if 'userMessage' in command_output:
            log.error('Network service creation failed with details :%s', command_output)
            Report_file.add_line('Network service creation failed with details :' + command_output)
            assert False
        elif 'Internal Server Error' in command_output:
            log.error('*********************CHECK WITH SO TEAM *******************************')
            log.error('Network service creation failed with details :%s', command_output)
            Report_file.add_line('Network service creation failed with details :' + command_output)
            log.error('*********************INTERNAL SERVER ERROR  ******************************')
            assert False

        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)
        service_id = output['id']

    sit_data._SIT__network_service_id = service_id
    log.info('Creation of network service ends with service id %s', service_id)
    Report_file.add_line('Creation of network service ends with service id ' + service_id)


def get_sol_dummy_service_id(connection, so_dummy_depl_name, so_token, so_host):
    try:
        global so_host_name
        so_host_name = so_host
        log.info('Start to get Service Id')
        Report_file.add_line('Start to get Service Id')

        command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' "https://{}/orchestrationcockpit/eso/v1.0/services?offset=0&limit=50&sortAttr=name&sortDir=asc&filters="%"7B"%"22state"%"22:"%"22Active"%"22"%"7D"'''.format(
            so_token, so_host_name
        )
        Report_file.add_line('command :' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)
        total_items = output['total']
        if total_items != 0:
            item_list = output['items']
            for count in range(total_items):
                item_dict = item_list[count]
                package_name = item_dict['name']
                if so_dummy_depl_name in package_name:
                    global service_id
                    service_id = item_dict['id']
                    Report_file.add_line('Service Id - ' + service_id)
                    return service_id
            else:
                log.info('NO Active services available in Service Orchestration gui')
                Report_file.add_line('NO Active services available in Service Orchestration gui')
                assert False

    except Exception as e:
        log.error('Failed to get service id %s', str(e))
        Report_file.add_line('Failed to get service id' + str(e))
        assert False


def poll_status_so():
    """
     This so version we are fetching just for getting the create service status for new APIs
    This way we need not to handle fetching the version in each usecase if it is there or not
    node name -- "Service_status" just in this case
    """
    poll_so_version = fetch_so_version("Service_status")
    check_so_network_service_state(poll_so_version)


def check_so_user_accessibility(entity_name, connection, command, user):
    log.info(f'Checking if the {entity_name} accessible from  {user}')
    Report_file.add_line(f'Checking if the {entity_name} accessible from  {user}')
    log.info(command)
    Report_file.add_line('command : ' + command)
    # do not use generic method to run curl command as we need Access denied in output in negative testcase
    # please check the calling method for details
    stdin, stdout, stderr = connection.exec_command(command)
    command_output = str(stdout.read())
    Report_file.add_line('command output :' + command_output)
    return command_output


def fetch_external_subnet_id():
    ecm_connection = None
    try:

        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        core_vm_ip = Server_details.ecm_host_blade_corevmip(Server_details)
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname
        external_network_id = sit_data._SIT__external_net_id

        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        token = Common_utilities.authToken(Common_utilities, ecm_connection, core_vm_hostname)

        command = '''curl --insecure "https://{}/ecm_service/v2/vns" -H "Accept: application/json" -H "AuthToken: {}"'''.format(
            core_vm_hostname, token
        )

        Report_file.add_line('command to get subnet_id of external network from ECM ' + command)
        command_output = ExecuteCurlCommand.get_json_output(ecm_connection, command)
        command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

        output = ast.literal_eval(command_out)

        requestStatus = output['status']['reqStatus']

        if 'SUCCESS' in requestStatus:

            vns_list = output['data']['vns']

            for vn in vns_list:
                vim_object_id = vn['vimObjectId']
                if external_network_id == vim_object_id:
                    external_network_system_id = vn['id']
                    sub_networks = vn['subnets']
                    for sub_net in sub_networks:
                        ip_version = sub_net['ipVersion']
                        if ip_version == 'IPv4':
                            sub_network_id = sub_net['vimObjectId']
                            sub_network_system_id = sub_net['id']
                            Report_file.add_line(
                                'sub network id and external network id  '
                                + sub_network_id
                                + ' '
                                + external_network_id
                            )
                            break
                    break
            else:
                Report_file.add_line('external network id not found ' + external_network_id)
                assert False

            return external_network_id, sub_network_id, external_network_system_id, sub_network_system_id

        else:

            log.error('Failed to fetch the virtual networks details  ')
            Report_file.add_line('Failed to fetch the virtual networks details')
            assert False

    except Exception as e:
        log.error('Error SOL BGF deploy hot package %s', str(e))
        Report_file.add_line('Error SOL BGF deploy hot package ' + str(e))
        assert False

    finally:
        ecm_connection.close()


def check_state_action_service(connection, command, action_id):
    command_output = ExecuteCurlCommand.get_json_output(connection, command)
    command_out = ExecuteCurlCommand.get_sliced_command_output(command_output)

    if 'Service Unavailable' in command_out:
        log.error('*********************CHECK WITH SO TEAM *******************************')
        log.error('Error while running curl on SO : %s', command_out)
        log.error('*********************SERVICE UNAVAILABLE  ******************************')
        Report_file.add_line('Error while running curl on SO  :' + command_out)
        return command_out

    command_out = ast.literal_eval(command_out)

    name = command_out["name"]
    state = command_out["state"]

    if name == 'scale':
        state = command_out["state"]
        if state == '':
            log.info('Scale state not found')
            return 'Not Found'
        return state
    else:
        log.info('scale name not found')
        return 'Not Found'


def action_status_so(connection, token, host_name, action_id):
    log.info('Start to check Action status of Scale')

    Report_file.add_line('Start to check Action status of Scale')

    timeout = 60
    curl = '''curl -k -X GET -H 'cookie: JSESSIONID="{}"' -H 'Content-Type: application/json' -H 'Accept: application/json' https://{}/orchestration/v1/actions/{}'''.format(
        token, host_name, action_id
    )

    command = curl
    log.info(command)
    Report_file.add_line('command :' + command)
    while timeout != 0:

        state = check_state_action_service(connection, command, action_id)

        if 'Service Unavailable' in state:
            log.info('waiting 30 seconds to check again the state')
            time.sleep(30)
        elif 'Completed' in state:
            log.info('Scale action is created successfully with state %s', state)
            Report_file.add_line('Scale action is created successfully with state ' + state)
            connection.close()
            break
        elif 'InProgress' in state:
            log.info('Scale action creation ongoing with state %s', state)
            Report_file.add_line('Scale action creation ongoing with state ' + state)
            log.info('waiting 120 seconds to check again the state')
            timeout = timeout - 2
            time.sleep(120)

        elif 'Not Found' in state:
            log.error('Scale action is not created , check the SO logs ')
            Report_file.add_line('Scale action is not created ,check the SO logs ')
            connection.close()
            assert False
        else:
            log.error('Scale Action state %s', state)
            log.error('Error in Action Service Creation , check the SO logs')
            Report_file.add_line('Error in Scale action Creation , check the SO logs')
            connection.close()
            assert False
    if timeout == 0:
        log.info(f'Automation script timed out after {timeout} minutes, Action Service state : %s', state)
        Report_file.add_line(
            f'Automation script timed out after {timeout} minutes, Action Service state : ' + state
        )
        assert False


def onboard_sol_config_template(
        nsparam_form_name, ns_param_file, vnfparam_form_name, vnf_param_file, so_version, key_check=True
):
    connection = None
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)

        if vnf_param_file == 'epgAdditionalParams.json':
            epg_software_path = sit_data._SIT__epgEtsiNsdSoftwarePath
        else:
            epg_software_path = sit_data._SIT__epgSoftwarePath

        is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)
        vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace
        so_host_name = sit_data._SIT__so_host_name

        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        if key_check:

            if 'TRUE' == is_vm_vnfm:
                connection = get_VMVNFM_host_connection()
                cmd = "sudo -u jboss_user cat /vnflcm-ext/backups/workflows/private_keys/default/.ssh/id_rsa.pub"
                command = get_vmvnfm_pod_cmd(cmd)
                Report_file.add_line('admin authorize key command :' + command)
                stdin, stdout, stderr = connection.exec_command(command)

            else:
                connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
                command = 'sudo -u jboss_user cat /vnflcm-ext/backups/workflows/private_keys/default/.ssh/id_rsa.pub'
                Report_file.add_line('admin authorize key command :' + command)
                stdin, stdout, stderr = connection.exec_command(command, get_pty=True)

            command_output = str(stdout.read())
            Report_file.add_line('admin authorize key command output : ' + command_output)

            key = command_output[2:-5:1]

            log.info('closing lcm connection after fetching key')

            connection.close()
            # check for node type
            if vnf_param_file != 'epgAdditionalParams.json':
                update_vnf_param_file(vnf_param_file, key)

        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        if vnf_param_file != 'epgAdditionalParams.json':
            ServerConnection.put_file_sftp(
                connection,
                r'com_ericsson_do_auto_integration_files/' + ns_param_file,
                SIT.get_base_folder(SIT) + ns_param_file,
            )
            ServerConnection.put_file_sftp(
                connection,
                r'com_ericsson_do_auto_integration_files/' + vnf_param_file,
                SIT.get_base_folder(SIT) + vnf_param_file,
            )
        elif vnf_param_file == 'epgAdditionalParams.json':
            ServerConnection.get_file_sftp(connection, epg_software_path + '/so-artifacts/epgAdditionalParams.json',
                                           r'com_ericsson_do_auto_integration_files/epgAdditionalParams.json')

        so_token = Common_utilities.generate_so_token(
            Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
        )
        curl = ExecuteCurlCommand.curl_onboard_so_template(
            so_version, ns_param_file, nsparam_form_name, so_host_name, so_token, 'CONFIG_TEMPLATE', '-i'
        )

        if vnf_param_file != 'epgAdditionalParams.json':
            base_dir = SIT.get_base_folder(SIT)
        else:
            # command = 'cd ' + epg_software_path + '/so-artifacts; ' + curl
            base_dir = epg_software_path + '/so-artifacts'

        log.info('ns param command :%s', curl)
        Report_file.add_line('ns param command :' + curl)

        output = ExecuteCurlCommand.get_json_output(connection, curl, base_folder=base_dir)

        log.info('ns param command output : %s', output)
        Report_file.add_line('ns param command output : ' + output)

        if so_version < version.parse('2.11.0-551'):
            if '201 Created' in output:
                log.info('Successfully onboarded the nsparam')
                Report_file.add_line('Successfully onboarded the nsparam')
            else:
                log.error('Error onboarding nsparam ')
                Report_file.add_line('Error onboarding nsparam')
                assert False
        else:
            if "202 Accepted" not in output:
                log.error('Error onboarding nsparam')
                Report_file.add_line('Error onboarding nsparam')
                assert False
            # extract dictionary from response output
            out_dict = ast.literal_eval(re.search('({.+})', output).group(0))
            job_id = out_dict['jobId']

            curl = (
                f'curl -X GET --insecure -H "content-type: application/json" -H "cookie: JSESSIONID={so_token}"'
                f' https://{so_host_name}/onboarding/v3/jobs/{job_id}'
            )
            log.info('command :%s', curl)
            timeout = 60
            while timeout >= 0:
                job_response = ExecuteCurlCommand.get_json_output(connection, curl)
                log.info('command output : %s', job_response)
                job_response_out = ExecuteCurlCommand.get_sliced_command_output(job_response)
                if not job_response_out:
                    log.error('Error fetching job response')
                    Report_file.add_line(f'Error fetching job response')
                    assert False
                job_output = ast.literal_eval(job_response_out)

                if job_output['status'] == 'COMPLETED':
                    log.info('Successfully onboarded the nsparam')
                    break
                elif job_output['status'] == "FAILED":
                    log.error('Error onboarding nsparam')
                    Report_file.add_line('Error onboarding nsparam')
                    assert False
                elif timeout <= 0:
                    log.error('onboarding nsparam response timed out, status is: %s', job_output['status'])
                    Report_file.add_line(
                        'onboarding nsparam response timed out, status is: ' + job_output['status']
                    )
                    assert False
                elif job_output['status'] == 'IN_PROGRESS':
                    time.sleep(4)
                    timeout = timeout - 4

        curl = ExecuteCurlCommand.curl_onboard_so_template(
            so_version, vnf_param_file, vnfparam_form_name, so_host_name, so_token, 'CONFIG_TEMPLATE', '-i'
        )

        if vnf_param_file != 'epgAdditionalParams.json':
            base_dir = SIT.get_base_folder(SIT)
        else:
            # command = 'cd ' + epg_software_path + '/so-artifacts; ' + curl
            base_dir = epg_software_path + '/so-artifacts'

        Report_file.add_line('vnf param command :' + curl)
        log.info('vnf param command : %s', curl)
        output = ExecuteCurlCommand.get_json_output(connection, curl, base_folder=base_dir)

        Report_file.add_line('vnf param command output : ' + output)

        if so_version < version.parse('2.11.0-551'):
            if '201 Created' in output:
                log.info('Successfully onboarded the %s', vnfparam_form_name)
                Report_file.add_line('Successfully onboarded the ' + vnfparam_form_name)
            else:
                log.error('Error onboarding %s', vnfparam_form_name)
                Report_file.add_line('Error onboarding ' + vnfparam_form_name)
                assert False
        else:
            if "202 Accepted" not in output:
                log.error('Error onboarding %s', vnfparam_form_name)
                Report_file.add_line('Error onboarding ' + vnfparam_form_name)
                assert False
            out_dict = ast.literal_eval(re.search('({.+})', output).group(0))
            job_id = out_dict['jobId']
            curl = (
                f'curl -X GET --insecure -H "content-type: application/json" -H "cookie: JSESSIONID={so_token}"'
                f' https://{so_host_name}/onboarding/v3/jobs/{job_id}'
            )
            log.info('command :%s', curl)
            timeout = 60
            while timeout >= 0:
                job_response = ExecuteCurlCommand.get_json_output(connection, curl)
                log.info('command output : %s', job_response)
                job_response_out = ExecuteCurlCommand.get_sliced_command_output(job_response)
                if not job_response_out:
                    log.error('Error fetching job response')
                    Report_file.add_line(f'Error fetching job response')
                    assert False
                job_output = ast.literal_eval(job_response_out)

                if job_output['status'] == 'COMPLETED':
                    log.info('Successfully onboarded the %s', vnfparam_form_name)
                    Report_file.add_line('Successfully onboarded the' + vnfparam_form_name)
                    break
                elif job_output['status'] == 'FAILED':
                    log.error('Error onboarding %s', vnfparam_form_name)
                    Report_file.add_line('Error onboarding ' + vnfparam_form_name)
                    assert False
                elif timeout <= 0:
                    log.error('onboarding vnfparam response timed out, status is: %s', job_output['status'])
                    Report_file.add_line(
                        'onboarding vnfparam response timed out, status is: ' + job_output['status']
                    )
                    assert False
                elif job_output['status'] == 'IN_PROGRESS':
                    time.sleep(4)
                    timeout = timeout - 4

    except Exception as e:
        log.error('Error onboarding config sol template  %s', str(e))
        Report_file.add_line('Error onboarding config sol template  ' + str(e))
        assert False

    finally:
        connection.close()


def onboard_cnf_sol_configmap_templates(so_version, config_files):
    """
    Onboard all the required configuration files for cnf configmap deploy to SO
    config_files: is a dictionary
    {conf_file: conf_file_with_timestamp}
    """
    connection = None
    try:
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)
        so_deployment_type = SIT.get_so_deployment_type(SIT)
        so_host_name = SIT.get_so_host_name(SIT)
        username = EPIS.get_openstack_username(EPIS)
        password = EPIS.get_openstack_password(EPIS)
        openstack_ip = EPIS.get_openstack_ip(EPIS)

        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        if so_deployment_type == 'IPV6':
            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)
        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        for file, template_filename in config_files.items():
            ServerConnection.put_file_sftp(
                connection, r'com_ericsson_do_auto_integration_files/' + file, SIT.get_base_folder(SIT) + file
            )
            so_token = Common_utilities.generate_so_token(
                Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
            )

            command = ExecuteCurlCommand.curl_onboard_so_template(
                so_version, file, template_filename, so_host_name, so_token, 'CONFIG_TEMPLATE', '-i'
            )

            output = ExecuteCurlCommand.get_json_output(connection, command)
            log.info('%s onboard command output : %s', template_filename, output)

            if so_version < version.parse('2.11.0-551'):
                if '201 Created' in output:
                    log.info('Successfully on-boarded the %s', template_filename)
                else:
                    log.error('Error on-boarding %s', template_filename)
                    assert False
            else:
                if "202 Accepted" not in output:
                    log.error('Error on-boarding %s', template_filename)
                    assert False
                out_dict = ast.literal_eval(re.search('({.+})', output).group(0))
                job_id = out_dict['jobId']
                curl = (
                    f'curl -X GET --insecure -H "content-type: application/json" -H "cookie: JSESSIONID={so_token}"'
                    f' https://{so_host_name}/onboarding/v3/jobs/{job_id}'
                )
                timeout = 60
                while timeout >= 0:
                    job_response = ExecuteCurlCommand.get_json_output(connection, curl)
                    log.info('command output : %s', job_response)
                    job_response_out = ExecuteCurlCommand.get_sliced_command_output(job_response)
                    if not job_response_out:
                        log.error('Error fetching job response')
                        assert False
                    job_output = ast.literal_eval(job_response_out)
                    if job_output['status'] == 'COMPLETED':
                        log.info('Successfully on-boarded the %s', template_filename)
                        break
                    elif job_output['status'] == 'FAILED':
                        log.error('Error on-boarding %s', template_filename)
                        assert False
                    elif timeout <= 0:
                        log.error('onboarding vnfparam response timed out, status is: %s', job_output['status'])
                        assert False
                    elif job_output['status'] == 'IN_PROGRESS':
                        time.sleep(4)
                        timeout = timeout - 4

    except Exception as error:
        log.error('Error on-boarding CNF Config sol template  %s', str(error))
        assert False

    finally:
        connection.close()


def onboard_day1_template(software_path, node_name, so_version):
    connection = None
    try:
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        so_deployment_type = sit_data._SIT__so_deployment_type
        so_host_name = sit_data._SIT__so_host_name

        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openstack_ip = EPIS_data._EPIS__openstack_ip
        if node_name != 'TEPG':
            day1_file_path = software_path + '/so-artifacts/' + 'day1Config' + node_name + '_new.xml'
            day1_file_name = 'day1Config' + node_name + '_new.xml'
        else:
            day1_file_path = software_path + '/so-artifacts/' + 'day1Config' + node_name + '.xml'
            day1_file_name = 'day1Config' + node_name + '.xml'

        if so_deployment_type == 'IPV6':
            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        try:
            log.info('getting day1 file from blade software path')
            ServerConnection.get_file_sftp(
                connection, day1_file_path, r'com_ericsson_do_auto_integration_files/' + day1_file_name
            )

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path: %s', day1_file_path)
            assert False

        log.info('putting file on blade root')

        ServerConnection.put_file_sftp(
            connection, r'com_ericsson_do_auto_integration_files/' + day1_file_name,
                        SIT.get_base_folder(SIT) + day1_file_name
        )

        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        so_token = Common_utilities.generate_so_token(
            Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
        )

        global day1_template_name
        day1_template_name = Common_utilities.get_name_with_timestamp(
            Common_utilities, node_name + '_day1_template'
        )

        sit_data._SIT__day1_template_name = day1_template_name

        curl = ExecuteCurlCommand.curl_onboard_so_template(
            so_version, day1_file_name, day1_template_name, so_host_name, so_token, 'CONFIG_TEMPLATE', '-i'
        )

        command = curl
        log.info(command)
        Report_file.add_line('onboard day1 template command :' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)
        Report_file.add_line('command output :' + command_output)

        log.info('Finished Onboarding of day1 template using catalog manager')
        Report_file.add_line('finished Onboarding of day1 template using catalog manager ')

    except Exception as e:
        log.error('Error on-boarding day1 template  %s', str(e))
        Report_file.add_line('Error on-boarding day1 template  ' + str(e))
        assert False

    finally:
        connection.close()


def onboard_ecm_template(software_path, node_name, so_version):
    connection = None
    try:
        log.info('start onboarding ecm template  ')
        Report_file.add_line('start onboarding ecm template')
        sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
        EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        so_deployment_type = sit_data._SIT__so_deployment_type
        so_host_name = sit_data._SIT__so_host_name

        username = EPIS_data._EPIS__openstack_username
        password = EPIS_data._EPIS__openstack_password
        openstack_ip = EPIS_data._EPIS__openstack_ip

        ecm_template_path = software_path + '/so-artifacts/' + 'EcmTemplate' + node_name + '_new.txt'
        ecm_file_name = 'EcmTemplate' + node_name + '_new.txt'

        if so_deployment_type == 'IPV6':
            log.info('SO Deployment type is IPV6, connecting with open stack ')
            connection = ServerConnection.get_connection(openstack_ip, username, password)

        else:
            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

        try:
            log.info('getting ecm template file from blade software path')
            ServerConnection.get_file_sftp(
                connection, ecm_template_path, r'com_ericsson_do_auto_integration_files/' + ecm_file_name
            )

        except FileNotFoundError:
            log.error('File Not Found Error. Wrong file or file path: %s', ecm_template_path)
            assert False

        log.info('putting file on blade root')
        ServerConnection.put_file_sftp(
            connection, r'com_ericsson_do_auto_integration_files/' + ecm_file_name,
                        SIT.get_base_folder(SIT) + ecm_file_name
        )

        global ecm_template_name
        ecm_template_name = Common_utilities.get_name_with_timestamp(
            Common_utilities, node_name + '_ecm_template'
        )

        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        so_token = Common_utilities.generate_so_token(
            Common_utilities, connection, so_host_name, token_user, token_password, token_tenant
        )

        curl = ExecuteCurlCommand.curl_onboard_so_template(
            so_version, ecm_file_name, ecm_template_name, so_host_name, so_token, 'CONFIG_TEMPLATE'
        )

        command = curl
        log.info(command)
        Report_file.add_line('onboard ecm template command :' + command)
        command_output = ExecuteCurlCommand.get_json_output(connection, command)

        Report_file.add_line('command output :' + command_output)

    except Exception as e:
        log.error('Error on-boarding ecm template  %s', str(e))
        Report_file.add_line('Error onboarding ecm template ' + str(e))
        assert False

    finally:
        connection.close()
