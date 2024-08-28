import paramiko
import time
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.SIT_files_update import update_runtime_env_file
from com_ericsson_do_auto_integration_initilization.Initialization_script import Initialization_script
from com_ericsson_do_auto_integration_initilization.ECM_PI_initialization import ECM_PI_Initialization
from com_ericsson_do_auto_integration_scripts.ECM_NODE_DEPLOYMENT import *
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
import os

log = Logger.get_logger('LCM_POST_INSTALLATION.py')


def change_password_first_login(project_type):
    try:
        log.info('Start changing password for first login on vnf-lcm')
        curr_pass = 'passw0rd'
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        if 'static' in project_type:

            server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP

        else:
            server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP

        user_name = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        log.info('removing old entry of vnflcm from host file')

        os_command = 'ssh-keygen -R {}'.format(server_ip)
        os.system(os_command)

        ssh_conn = paramiko.SSHClient()
        ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_conn.load_system_host_keys()
        password_set = False

        try:
            ssh_conn.connect(hostname=server_ip, username=user_name, password=curr_pass)
        except Exception as e:
            log.info('Password is already set to the new')
            password_set = True

        if not password_set:
            interact = ssh_conn.invoke_shell()
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            time.sleep(5)
            # if 'UNIX password:' in buff :
            interact.send(curr_pass + '\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'New password:' in buff:
                interact.send(password + '\n')

            time.sleep(5)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'Retype new password' in buff:
                interact.send(password + '\n')
            time.sleep(5)
            interact.shutdown(2)
            if interact.exit_status_ready():
                log.info("EXIT STATUS :" + str(interact.recv_exit_status()))

            log.info('successfully changed the password for vnf-lcm at first login')
    except Exception as e:
        log.error('Error while changing the password for vnf-lcm at first login')
        Report_file.add_line('Error while changing the password for vnf-lcm at first login')
        assert False


def change_password_first_login_standby():
    core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
    deployment_type = core_vm_data._Ecm_PI__deployment_type
    if deployment_type == 'HA':
        try:
            log.info('Start changing password for first login on  standby vnf-lcm')
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

            server_vip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
            vip_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
            vip_passwd = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
            dynamic_server_ip1 = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Service_IP1

            connection = ServerConnection.get_connection(server_vip, vip_username, vip_passwd)
            interact = connection.invoke_shell()
            resp = interact.recv(9999)
            buff = str(resp)
            command = 'ifconfig eth1 | grep inet'

            interact.send(command + '\n')
            time.sleep(3)
            resp = interact.recv(9999)
            buff = str(resp)

            if dynamic_server_ip1 in buff:
                standby_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Service_IP
            else:
                standby_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Service_IP1

            log.info('Start changing password for first login on  standby vnf-lcm' + standby_ip)

            user_name = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
            password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
            curr_pass = 'passw0rd'

            ssh_conn = paramiko.SSHClient()
            ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_conn.load_system_host_keys()

            password_set = False

            try:
                ssh_conn.connect(hostname=standby_ip, username=user_name, password=curr_pass)
            except Exception as e:
                log.info('Password is already set to the new from default')
                password_set = True

            if not password_set:
                interact = ssh_conn.invoke_shell()
                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                time.sleep(5)
                # if 'UNIX password:' in buff :
                interact.send(curr_pass + '\n')
                time.sleep(5)
                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                if 'New password:' in buff:
                    interact.send(password + '\n')

                time.sleep(5)

                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                if 'Retype new password' in buff:
                    interact.send(password + '\n')
                time.sleep(5)
                interact.shutdown(2)
                if interact.exit_status_ready():
                    log.info("EXIT :", interact.recv_exit_status())

                log.info('successfully changed the password for standby vnf-lcm at first login' + standby_ip)
        except Exception as e:
            log.error('Error while changing the password for standby vnf-lcm at first login for:')
            Report_file.add_line('Error while changing the password for standby vnf-lcm at first login')
            assert False
    else:
        log.info('Standby server password change is not applicable for NON-HA server:')
        Report_file.add_line('Standby server password change is not applicable for NON-HA server')


def lcm_workflow_deployment(project_type):
    try:

        log.info('Start to deploy vnflcm workflow')
        log.info('start workflow bundle install on LCM')
        Report_file.add_line('Workflow  bundle install on LCM begins...')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        if 'static' in project_type:

            server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP

        else:
            server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP

        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        rpm_link = ecm_host_data._Ecm_core__rpm_bundle_link

        connection = ServerConnection.get_connection(server_ip, username, password)

        log.info('Downloading RPM bundle file using the link provided in the DIT:' + rpm_link)
        Report_file.add_line('Downloading rpm bundle file using the link provided in DIT')
        command = 'wget {}'.format(rpm_link)
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())
        log.info('command output ' + command_output)

        command = 'find ERICvnflaf*.rpm | xargs ls -rt | tail -1'
        stdin, stdout, stderr = connection.exec_command(command)

        command_output = str(stdout.read())[2:-3:]
        log.info(command_output)

        if command_output.startswith('ERICvnflaf') and command_output.endswith('.rpm'):
            rpmname = command_output
        else:
            log.info('ERICvnflaf*.rpm No such file.Hence making the job to failure state')
            Report_file.add_line('ERICvnflaf*.rpm No such file.Hence making the job to failure state')
            assert False 
       
        log.info('rpm name :' + rpmname)
        log.info('Workflow rpm file downloaded is: ' + command_output)
        Report_file.add_line('Workflow rpm  bundlefile downloaded succesfully.')

        command = 'sudo -i wfmgr bundle install --package=/home/cloud-user/{}'.format(rpmname)

        LCM_workflow_installation_validation(connection, command, 'DUMMY')
        Common_utilities.clean_up_rpm_packages(Common_utilities, connection, rpmname)

        connection.close()
    except Exception as e:
        connection.close()
        log.error('Error workflow bundle install on LCM')
        Report_file.add_line('Error workflow bundle install on LCM')
        assert False


def install_nfvo_tls_ceritificates():
    try:

        log.info('Start installing NFVO TLS Certs ')
        Report_file.add_line('Start installing NFVO TLS Certs ')
        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')

        lcm_server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
        lcm_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        lcm_password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
        core_vm_hostname = ecm_host_data._Ecm_core__core_vm_hostname

        core_vm_username = core_vm_data._Ecm_PI__CORE_VM_USERNAME
        core_vm_password = core_vm_data._Ecm_PI__CORE_VM_PASSWORD
        deployment_type = core_vm_data._Ecm_PI__deployment_type

        if deployment_type == 'HA':
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_HA_IP
        else:
            core_vm_ip = core_vm_data._Ecm_PI__CORE_VM_IP

        connection = ServerConnection.get_connection(core_vm_ip, core_vm_username, core_vm_password)
        interact = connection.invoke_shell()
        log.info('transferring ecm_ssl.crt to VNF_LCM server')

        destination = lcm_username + '@' + lcm_server_ip

        command = 'scp /etc/pki/tls/certs/ecm_ssl.crt ' + destination + ':/home/cloud-user/'
        log.info(command)

        interact.send(command + '\n')
        time.sleep(5)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'continue connecting' in buff:
            interact.send('yes\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)

        if 'password' in buff:
            interact.send(lcm_password + '\n')

        time.sleep(5)
        interact.shutdown(2)
        connection.close()
        log.info('Core_VM_Connection close ' + core_vm_ip)

        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)
        command = 'sudo -i cp /home/cloud-user/ecm_ssl.crt /etc/pki/ca-trust/source/anchors/'
        log.info(command)
        connection.exec_command(command, get_pty=True)
        time.sleep(2)
        log.info('ecm_ssl.crt transferred to /etc/pki/ca-trust/source/anchors/ ')

        command = 'sudo update-ca-trust extract'
        log.info(command)
        connection.exec_command(command, get_pty=True)
        time.sleep(2)
        log.info('ecm_ssl.crt extracted ')

        log.info(
            'installing other certificate - https://confluence-nam.lmera.ericsson.se/display/ESO/VNFLCM+Config+in+EOCM  ')
        interact = connection.invoke_shell()
        command = 'sudo -i'
        interact.send(command + '\n')
        time.sleep(2)
        command = 'openssl s_client -showcerts -connect ' + core_vm_hostname + ':443 < /dev/null | openssl x509 -outform DER > /tmp/ecm_cert.cer'
        log.info(command)
        interact.send(command + '\n')
        time.sleep(3)
        command = '/usr/java/jdk1.8.0_172/bin/keytool -import -alias EO_Stageing -file /tmp/ecm_cert.cer -keystore /usr/java/jdk1.8.0_172/jre/lib/security/cacerts -storepass changeit'
        log.info(command)
        interact.send(command + '\n')
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'Certificate already exists' in buff:
            interact.send('no\n')
            time.sleep(2)
        time.sleep(2)
        interact.shutdown(2)
        connection.close()
        log.info('LCM Connection close ' + lcm_server_ip)

    except Exception as e:
        connection.close()
        log.error('Error installing NFVO TLS Certs  ' + str(e))
        Report_file.add_line('Error installing NFVO TLS Certs  ' + str(e))
        assert False


def create_auth_file_vnflcm():
    try:

        log.info('transferring auth.josn to VNF_LCM server')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
        # standby_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Service_IP1
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        file_name = 'auth.json'
        log.info('transferring auth.json file to /var/www/html/ ' + server_ip)

        connection = ServerConnection.get_connection(server_ip, username, password)

        ServerConnection.put_file_sftp(connection, file_name, r'/home/cloud-user/auth.json')

        command = 'sudo -i cp /home/cloud-user/auth.json /var/www/html/auth.json'
        connection.exec_command(command, get_pty=True)
        time.sleep(2)
        connection.close()
        log.info('Auth.json File transferred to /var/www/html/ ' + server_ip)

        core_vm_data = ECM_PI_Initialization.get_model_objects(ECM_PI_Initialization, 'ECMPI')
        deployment_type = core_vm_data._Ecm_PI__deployment_type
        if deployment_type == 'HA':
            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
            server_vip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
            vip_username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
            vip_passwd = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password
            dynamic_server_ip1 = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Service_IP1

            connection = ServerConnection.get_connection(server_vip, vip_username, vip_passwd)
            interact = connection.invoke_shell()
            resp = interact.recv(9999)
            buff = str(resp)
            command = 'ifconfig eth1 | grep inet'

            interact.send(command + '\n')
            time.sleep(3)
            resp = interact.recv(9999)
            buff = str(resp)

            if dynamic_server_ip1 in buff:

                standby_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Service_IP
            else:

                standby_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Service_IP1

            log.info('transferring auth.json file to /var/www/html/ ' + standby_ip)
            connection = ServerConnection.get_connection(standby_ip, username, password)

            ServerConnection.put_file_sftp(connection, file_name, r'/home/cloud-user/auth.json')

            command = 'sudo -i cp /home/cloud-user/auth.json /var/www/html/auth.json'
            connection.exec_command(command, get_pty=True)
            time.sleep(2)
            connection.close()
            log.info('Auth.json File transferred to /var/www/html/ ' + standby_ip)
        else:
            log.info('auth.json file transfer to standby server is not required for NON-HA server')
            Report_file.add_line('auth.json file transfer to standby server is not required for NON-HA server:  ')



    except Exception as e:
        connection.close()
        log.error('Error transfer auth.json file  ' + str(e))
        Report_file.add_line('Error transfer auth.json file  ' + str(e))
        assert False


def create_vnf_gui_user():
    try:
        log.info('start creating VNF-LCM GUI user and password for VNF-LCM-EOCM-INT')
        Report_file.add_line('start creating VNF-LCM GUI user and password for VNF-LCM-EOCM-INT')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        connection = ServerConnection.get_connection(server_ip, username, password)

        vnf_lcm_version = Common_utilities.get_vnf_lcm_version(Common_utilities, connection)

        interact = connection.invoke_shell()
        time.sleep(2)
        command = 'sudo -i'
        interact.send(command + '\n')
        time.sleep(2)

        if vnf_lcm_version >= '5.12.20':
            command = '/opt/rh/jbcs-httpd24/root/bin/htpasswd -c /etc/htpasswd/.htpasswd ' + username
        else:
            command = 'htpasswd -c /etc/htpasswd/.htpasswd ' + username

        log.info(command)
        interact.send(command + '\n')
        time.sleep(3)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'New password:' in buff:
            interact.send(password + '\n')
            time.sleep(3)
            resp = interact.recv(9999)
            buff = str(resp)
        log.info(buff)

        if "Re-type new password" in buff:
            interact.send(password + '\n')
            time.sleep(3)

        if vnf_lcm_version >= '5.12.20':
            command = 'service jbcs-httpd24-httpd restart'
        else:
            command = 'service httpd restart'

        log.info(command)
        interact.send(command + '\n')
        time.sleep(3)
        interact.shutdown(2)
        connection.close()
        log.info('Finished creating VNF-LCM GUI user and password for VNF-LCM-EOCM-INT')
        Report_file.add_line('Finished VNF-LCM GUI user and password for VNF-LCM-EOCM-INT')
    except Exception as e:
        connection.close()
        log.error('Error to create VNF-LCM GUI user and password for VNF-LCM-EOCM-INT')
        Report_file.add_line('Error to create VNF-LCM GUI user and password for VNF-LCM-EOCM-INT')
        assert False


def change_db_server_password(project_type):
    try:
        log.info('start changing VNF-LCM db server password at first login')
        Report_file.add_line('start changing VNF-LCM db server password at first login')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')
        if 'static' in project_type:

            server_ip = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_IP

        else:
            server_ip = ecm_host_data._Ecm_core__VNF_LCM_dynamic_Servicedb_IP
        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        old_password = 'passw0rd'

        ssh_conn = paramiko.SSHClient()
        ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh_conn.load_system_host_keys()

        password_set = False
        try:
            ssh_conn.connect(hostname=server_ip, username=username, password=password)
            log.info('VNFLCM password is changed from defualt')
        except Exception as e:
            log.info('VNFLCM password is not changed from default. Proceeding to change password')
            password_set = True

        if password_set:
            ssh_conn.connect(hostname=server_ip, username=username, password=old_password)
            log.info('Logging to VNFLCM server to change the password from default')

            interact = ssh_conn.invoke_shell()
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            time.sleep(5)
            # if 'UNIX password:' in buff :
            interact.send(old_password + '\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'New password:' in buff:
                interact.send(password + '\n')

            time.sleep(5)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'Retype new password' in buff:
                interact.send(password + '\n')
            time.sleep(5)
            interact.shutdown(2)
            if interact.exit_status_ready():
                log.info("EXIT :", interact.recv_exit_status())

            log.info('successfully changed the password for  vnf-lcm at first login' + server_ip)

        log.info('Logging to VNFLCM with the new password and Proceeding to change the Service DB pasword')
        connection = ServerConnection.get_connection(server_ip, username, password)
        interact = connection.invoke_shell()
        time.sleep(2)
        command = 'sudo -i'
        interact.send(command + '\n')
        time.sleep(2)
        command = 'sshdb'
        interact.send(command + '\n')
        time.sleep(6)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        if 'want to continue' in buff:
            interact.send('yes' + '\n')
            time.sleep(3)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
        if "vnflaf-db's password" in buff:
            interact.send(old_password + '\n')
            time.sleep(4)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'Permission denied' in buff:
                log.info('DB password is already set to new password')
            else:
                if 'UNIX password' in buff:
                    interact.send(old_password + '\n')
                    time.sleep(4)

                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                if 'New password:' in buff:
                    interact.send(password + '\n')
                    time.sleep(5)

                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                if 'Retype new password' in buff:
                    interact.send(password + '\n')
                    time.sleep(5)

                resp = interact.recv(9999)
                buff = str(resp)
                log.info(buff)
                interact.shutdown(2)

        connection.close()

        log.info('Finished changing VNF-LCM db server password at first login')
        Report_file.add_line('Finished changing VNF-LCM db server password at first login')
    except Exception as e:
        connection.close()
        log.error('Error to update vnf-lcm db first login password')
        Report_file.add_line('Error to update vnf-lcm db first login password')
        assert False


def check_vnf_lcm_password(server_ip):
    try:
        log.info('start checking VNF-LCM server password at first login')
        Report_file.add_line('start checking VNF-LCM server password at first login')

        ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

        username = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Username
        password = ecm_host_data._Ecm_core__VNF_LCM_Servicedb_Password

        old_password = 'passw0rd'

        password_set = False
        try:
            connection = ServerConnection.get_connection(server_ip, username, password)
            log.info('Password of VNFLCM is already changed from default.')
            connection.close()

        except Exception as e:
            log.info('Password of vnflcm server is not changed from default')
            password_set = True

        if password_set:
            ssh_conn = paramiko.SSHClient()
            ssh_conn.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh_conn.load_system_host_keys()
            ssh_conn.connect(hostname=server_ip, username=username, password=old_password)

            interact = ssh_conn.invoke_shell()
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            time.sleep(5)
            # if 'UNIX password:' in buff :
            interact.send(old_password + '\n')
            time.sleep(5)
            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'New password:' in buff:
                interact.send(password + '\n')

            time.sleep(5)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)
            if 'Retype new password' in buff:
                interact.send(password + '\n')
            time.sleep(5)
            interact.shutdown(2)
            if interact.exit_status_ready():
                log.info("EXIT :", interact.recv_exit_status())

            log.info('successfully changed the password for vnf-lcm service at first login')


    except Exception as e:
        log.error('Error to connect to VNF-LCM')
        Report_file.add_line('Error connecting to VNF-LCM')
        assert False


def fetch_vnf_manager_id():
    try:
        log.info('start fetching vnf manager id')
        Report_file.add_line('start fetching vnf manager id')

        lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)

        connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

        interact = connection.invoke_shell()

        command = 'sudo -i'
        interact.send(command + '\n')
        time.sleep(2)

        command = 'sshdb'
        interact.send(command + '\n')

        time.sleep(6)
        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        if "vnflaf-db's password" in buff:
            interact.send(lcm_password + '\n')
            time.sleep(4)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        command = '''sudo -u postgres psql -d vnflafdb '''
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)

        command = 'select subscriptionid from nfvo where nfvoinuse = {}Y{};'.format("'", "'")
        Report_file.add_line('vnf manager id fetch command ' + command)
        interact.send(command + '\n')
        time.sleep(2)

        resp = interact.recv(9999)
        buff = str(resp)

        log.info(buff)

        output = buff.split(';')

        split_data = output[1]

        output = split_data.split('\\r\\n--------------------------------------')[1]

        vnf_manager_id = output.split('\\r\\n')[1].strip()

        Report_file.add_line('VNF Manager Id - ' + vnf_manager_id)

        interact.shutdown(2)
        update_runtime_env_file('VNF_MANAGER_ID', vnf_manager_id)

    except Exception as e:

        log.error('Error fetching vnf manager id' + str(e))
        Report_file.add_line('Error fetching vnf manager id ' + str(e))
        assert False
    finally:

        connection.close()

