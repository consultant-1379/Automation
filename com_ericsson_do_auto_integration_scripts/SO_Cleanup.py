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
from packaging import version

from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.SO_file_update import update_service_delete_file
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.SIT_initialization import SIT_initialization
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_scripts.SO_NODE_DEPLOYMENT import (check_entity_exists, check_new_entity_exists,
                                                                         delete_subsystems, fetch_so_version)
from com_ericsson_do_auto_integration_utilities.ExecuteCurlCommand import ExecuteCurlCommand

log = Logger.get_logger('SO_Cleanup.py')

so_host_name = ''
so_token = ''
staging_token = ''
so_deployment_type = ''


def delete_services(connection, total_items, item_list, so_version):
    """
    @param connection:
    @param total_items:
    @param item_list:
    @param so_version:
    """
    log.info('Start deleting services')
    Report_file.add_line('Start deleting services')
    cleanup_file = 'delete_service.json'
    for count in range(total_items):
        item_dict = item_list[count]
        id = item_dict['id']
        service_name = item_dict['name']

        if so_version >= version.parse('2.11.0-118'):
            update_service_delete_file(cleanup_file, id, service_name)
            ServerConnection.put_file_sftp(connection, r'com_ericsson_do_auto_integration_files/' + cleanup_file,
                                           SIT.get_base_folder(SIT) + cleanup_file)
            command = f'''curl --insecure -X POST -H 'cookie: JSESSIONID={so_token}' -H 'Content-Type: application/json' -H 'Accept: application/json' -d @{cleanup_file} https://{so_host_name}/service-order-mgmt/v1/serviceOrder'''

        else:
            command = '''curl -X DELETE --insecure 'https://{}/orchestration/v1/services/{}' -H 'Cookie: JSESSIONID="{}"{} '''.format(
                so_host_name, id, staging_token, "'")
        log.info(command)
        Report_file.add_line('command :' + command)
        log.info('Proceeding to delete service with id %s', id)
        Report_file.add_line('Proceeding to terminate service with id - ' + id)
        ExecuteCurlCommand.get_json_output(connection, command)
        log.info('waiting 20 seconds to going for next service id termination')
        time.sleep(20)
    log.info('Finished deleting services')
    Report_file.add_line('Finished deleting services')


def delete_subsytems(so_version):
    """
    @param so_version:
    """
    EPIS_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'EPIS')
    ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
    ecm_server_ip = ecm_host_data._Ecm_core__ECM_Host_Blade_IP
    ecm_username = ecm_host_data._Ecm_core__ECM_Host_Blade_username
    ecm_password = ecm_host_data._Ecm_core__ECM_Host_Blade_Password

    openstack_ip = EPIS_data._EPIS__openstack_ip
    username = EPIS_data._EPIS__openstack_username
    password = EPIS_data._EPIS__openstack_password
    token_user = 'so-user'
    token_password = 'Ericsson123!'
    token_tenant = 'master'

    if so_deployment_type == 'IPV6':

        log.info('SO Deployment type is IPV6, connecting with open stack ')
        connection = ServerConnection.get_connection(openstack_ip, username, password)

    else:
        connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)

    global so_token
    so_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                  token_password, token_tenant)

    command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/subsystem-manager/v1/subsystems'''.format(
        so_token, so_host_name)
    total_subs, subs_data = check_new_entity_exists('subsystems', connection, command)

    if total_subs != 0:
        token_user = 'staging-user'
        token_password = 'Testing12345!!'
        token_tenant = 'staging-tenant'

        global staging_token
        staging_token = Common_utilities.generate_so_token(Common_utilities, connection, so_host_name, token_user,
                                                           token_password, token_tenant)

        command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/orchestration/v1/services'''.format(
            staging_token, so_host_name)
        total_serv, serv_data = check_entity_exists('services', connection, command)

        if total_serv != 0:
            delete_services(connection, total_serv, serv_data, so_version)
            log.info('time out for this process is 60 mins')
            timeout = 3600

            while timeout != 0:
                command = '''curl --insecure --header 'Accept: application/json' --header 'Cookie: JSESSIONID="{}"' https://{}/orchestration/v1/services'''.format(
                    staging_token, so_host_name)
                total_serv, serv_data = check_entity_exists('services', connection, command)

                if total_serv != 0:
                    log.info(f'Waiting 60 sec for {total_serv} service to complete deletion')
                    timeout = timeout - 60
                    time.sleep(60)
                else:
                    log.info("All services have been deleted")
                    break

            if timeout == 0:
                log.info(f'Automation script timed out after 60 minutes. {total_serv} services still not deleted')
                Report_file.add_line(f'Automation script timed out after 60 minutes. {total_serv} services still not deleted')
                Report_file.add_line(serv_data)
                assert False

        else:
            log.info('No services exists on service orchestrator')
            Report_file.add_line('No services exists on service orchestrator')

        delete_subsystems(connection, total_subs, subs_data, so_host_name, so_token)
        log.info('waiting 10 seconds to complete deletion')
        time.sleep(10)
    else:
        log.info('No subsystems exists on service orchestrator')
        Report_file.add_line('No subsystems exists on service orchestrator')


def start_so_cleanup():
    """ So Cleanup """
    log.info('Start So cleanup activity')
    Report_file.add_line('Start So cleanup activity')
    sit_data = SIT_initialization.get_model_objects(SIT_initialization, 'SIT')
    staging_type = sit_data._SIT__vnf_type
    global so_host_name
    global so_deployment_type

    if 'APP_STAGING' == staging_type:
        log.info('staging type is app_staging')
        so_version = fetch_so_version('subsystem')
    else:
        log.info('staging type is eo_staging')
        so_version = fetch_so_version('Dummy')

    so_host_name = sit_data._SIT__so_host_name
    so_deployment_type = sit_data._SIT__so_deployment_type
    delete_subsytems(so_version)

    log.info('End So cleanup activity')
    Report_file.add_line('End So cleanup activity')
