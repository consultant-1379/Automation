#!/usr/bin/env python

import time
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details

log = Logger.get_logger('CCD.py')


openstack_ip, username, password, openrc_filename = \
            Server_details.openstack_host_server_details(Server_details)
directory_server_ip, directory_server_username = \
    Server_details.vm_vnfm_director_details(Server_details)

connection = ServerConnection.get_connection(openstack_ip, username, password)
ServerConnection.get_file_sftp(connection, r'/root/env06Files/eccd150-director-key', r'eccd150-director-key')

# we are reducing sleep time from 80 to 10 if any issue occurs try to make it 80 again
log.info('waiting for 10sec to get director key file')
time.sleep(10)
file_path = 'eccd150-director-key'
nested_conn = ServerConnection.get_nested_server_connection(connection, openstack_ip, directory_server_ip,
                                                            directory_server_username, file_path)
time.sleep(2)
command = 'cat /etc/eccd/eccd_image_version.ini | grep -i IMAGE_RELEASE'
log.info('command to fetch out CCD version %s', command)
stdin, stdout, stderr = nested_conn.exec_command(command)
ccd_version = stdout.read().decode("utf-8")
time.sleep(3)
log.info('ccd version %s', ccd_version)
time.sleep(2)
nested_conn.close()
connection.close()

log.info('updating jenkins artifactory file with image version')

with open(r'/proj/eiffel052_config_fem1s11/slaves/EO-STAGING-SLAVE-2/workspace/EO_STAGING_CCD_Artifactory/artifacts.properties', "w+") as f:
    f.write(ccd_version)
