from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
import json
from com_ericsson_do_auto_integration_utilities import file_utils
import time

log = Logger.get_logger('VNF_LCM_ENM')


def get_file_from_server(source, destination, server_ip, username, password):
    log.info('Start: fetching ' + source)
    print(type(server_ip))
    print(type(username))
    print(type(password))
    print(server_ip, username, password)
    Report_file.add_line('Start: fetching ' + source)

    connection = ServerConnection.get_connection(server_ip, username, password)
    ServerConnection.get_file_sftp(connection, source, destination)
    connection.close()

    log.info('End:  fetching ' + source)
    Report_file.add_line('End:  fetching ' + source)


def get_key_pair_file(server_ip, username, password):
    get_file_from_server('/var/tmp/private_key.pem', 'private_key.pem', server_ip, username, password)


def fetch_httpd_ips(server_ip, username, password):
    get_file_from_server('/home/cloud-user/sed.json', 'sed.json', server_ip, username, password)
    user_input_file = 'sed.json'
    lcm_service_data = Initialization_script.get_model_objects(Initialization_script, 'LCM_SERVICE')
    try:

        with open(user_input_file, 'r') as user_input:

            file_data = json.load(user_input)
            data = file_data['parameter_defaults']['httpd_internal_ip_list']
            httpd_ips_list = data.split(',')
            lcm_service_data.set_httpd_ips_list(lcm_service_data, httpd_ips_list)
            lcm_service_data._LCM_service__httpd_ips_list = httpd_ips_list

    except FileNotFoundError:
        log.error('File Not Found Error : Wrong file or file path : ' + user_input_file)
        assert False


def update_hosts_file(server_ip, username, password, enm_deployment_type='Feature_Test_Single', vnf_lcm_ip='',
                      connection=''):
    lcm_service_data = Initialization_script.get_model_objects(Initialization_script, 'LCM_SERVICE')

    file_path = 'private_key.pem'
    dest_username = 'cloud-user'
    if enm_deployment_type == 'Extra_Small_vENM':
        httpd_ips = [vnf_lcm_ip]
        vnf_ip = lcm_service_data._LCM_service__vnf_service_ip
        # connection = host_conn
    else:
        httpd_ips = lcm_service_data._LCM_service__httpd_ips_list
        vnf_ip = lcm_service_data._LCM_service__vnf_service_ip
        connection = ServerConnection.get_connection(server_ip, username, password)

    data = vnf_ip + ' svc-vnflcm'

    for dest_server_ip in httpd_ips:
        log.info('Start Updating the hosts file on HTTPD server ' + dest_server_ip)
        Report_file.add_line('Start Updating the hosts file on HTTPD server ' + dest_server_ip)

        nested_conn = ServerConnection.get_nested_server_connection(connection, server_ip, dest_server_ip,
                                                                    dest_username, file_path)

        sftp = nested_conn.open_sftp()
        sftp.get('/etc/hosts', 'hosts')
        sftp.close()

        hostfile = open('hosts', 'r')
        hostlist = hostfile.readlines()
        hostfile.close()
        found = False
        for line in hostlist:

            if 'svc-vnflcm' in line:

                if vnf_ip in line:
                    log.info('VNF_LCM server ip is already present in /etc/hosts file ' + vnf_ip)
                    Report_file.add_line('VNF_LCM server ip is already present in /etc/hosts file ' + vnf_ip)
                    found = True
                    break
                file_utils.replace('hosts', str(line), data + '\n')
                found = True
                break

            else:
                found = False

        if not found:
            hostfile = open('hosts', 'a')
            hostfile.write(data + "\n")
            hostfile.close()

        sftp = nested_conn.open_sftp()
        sftp.put('hosts', '/home/cloud-user/hosts')
        sftp.close()
        time.sleep(2)
        command = 'sudo -i cp /home/cloud-user/hosts /etc/hosts'
        nested_conn.exec_command(command, get_pty=True)
        command = 'sudo -i service httpd restart'
        nested_conn.exec_command(command, get_pty=True)
        log.info('VNF_LCM server ip successfully updated in /etc/hosts file ' + vnf_ip)
        Report_file.add_line('VNF_LCM server ip successfully updated in /etc/hosts file ' + vnf_ip)
        nested_conn.close()

    connection.close()

    log.info('Finished Updating the hosts file on HTTPD server ' + dest_server_ip)
    Report_file.add_line('Finished Updating the hosts file on HTTPD server ' + dest_server_ip)


def main():
    log.info('Starting script : Integration of VNF_LCM to ENM')
    Report_file.add_line('Starting script : Integration of VNF_LCM to ENM')
    lcm_service_data = Initialization_script.get_model_objects(Initialization_script, 'LCM_SERVICE')
    server_ip = lcm_service_data._LCM_service__lcm_service_ip
    username = lcm_service_data._LCM_service__lcm_user_name
    password = lcm_service_data._LCM_service__lcm_password
    get_key_pair_file(server_ip, username, password)
    fetch_httpd_ips(server_ip, username, password)
    update_hosts_file(server_ip, username, password)

    log.info('END script : Integration of VNF_LCM to ENM')
    Report_file.add_line('END script :Integration of VNF_LCM to ENM')
