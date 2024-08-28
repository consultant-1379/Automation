from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Common_utilities import Common_utilities
from com_ericsson_do_auto_integration_utilities.Shell_handler import ShellHandler
import time
log = Logger.get_logger('ECM_SESSION_UPDATE.py')



def import_updated_config_file_corevm(core_vm_2):
    try:
        log.info('Start importing open-am config file ')
        Report_file.add_line('Start importing open-am config file ')
        core_vm_ip, username, password = Server_details.core_vm_details(Server_details, core_vm_2=core_vm_2)
        log.info('Running for core_vm_ip ' + core_vm_ip)
        core_vm_connection = ServerConnection.get_connection(core_vm_ip, username, password)

        interact = core_vm_connection.invoke_shell()
        resp = interact.recv(9999)
        buff = str(resp)
        command = 'su - ecm_admin'
        interact.send(command + '\n')
        time.sleep(3)

        resp = interact.recv(9999)
        buff = str(resp)
        log.info(buff)
        success = False
        log.info('This will retry 4 times in case of Unexpected LDAP exception ')
        retry = 1
        while(retry !=5):

            command = 'cd /app/ecm/security/openAm/sso-tools/scripts ; ./import-config.sh'

            interact.send(command + '\n')
            time.sleep(12)

            resp = interact.recv(9999)
            buff = str(resp)
            log.info(buff)

            if 'Service Configuration was imported' in buff:
                log.info('Sucessfully imported  open-am config file')
                Report_file.add_line('Sucessfully imported  open-am config file')
                interact.shutdown(2)
                core_vm_connection.close()
                success = True
                break
            elif 'Unexpected LDAP exception occurred' in buff:
                log.info('Error occured going for retry times '+str(retry))
                log.info('waiting 30 second for retry again')
                time.sleep(30)
                retry = retry + 1
                success = False
            else:
                success = False
                break

        if success:
            log.info('Sucessfully imported  open-am config file')
        else:
            log.error('Somthing wrong in import  open-am config file')
            Report_file.add_line('Somthing wrong in import  open-am config file')
            assert False


    except Exception as e:

        log.error('Error importing open-am config file ' + str(e))
        Report_file.add_line('Error importing open-am config file  ' + str(e))
        assert False

def place_updated_config_file_corevm(core_vm_2):
    try:
        log.info('Start putting updated file on core_vm from ECM_host_blade server ')
        Report_file.add_line('Start putting updated file on core_vm from ECM_host_blade server ')
        ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

        ecm_connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)
        path_on_ecm = r'/var/tmp/OPENAM_CONFIG_FILE/exported-openam-config.xml'
        local_path = r'com_ericsson_do_auto_integration_files/exported-openam-config.xml'
        core_vm_file_path = r'/app/ecm/security/openAm/exported-openam-config.xml'
        ServerConnection.get_file_sftp(ecm_connection, path_on_ecm, local_path)

        time.sleep(2)

        ecm_connection.close()

        core_vm_ip, username, password = Server_details.core_vm_details(Server_details, core_vm_2=core_vm_2)
        core_vm_connection = ServerConnection.get_connection(core_vm_ip, username, password)
        ServerConnection.put_file_sftp(core_vm_connection, local_path, core_vm_file_path)

        time.sleep(2)

        log.info('giving ecm_admin ownership to file ')
        command = 'chown ecm_admin:ecm_admin {}'.format(core_vm_file_path)

        stdin, stdout, stderr = core_vm_connection.exec_command(command)

        time.sleep(2)

        core_vm_connection.close()

        log.info('Finished putting updated file on core_vm from ECM_host_blade server ')
        Report_file.add_line('Finished putting updated file on core_vm from ECM_host_blade server ')

    except Exception as e:

        log.error('Error putting updated file on core_vm from ECM_host_blade server '  + str(e))
        Report_file.add_line('Error putting updated file on core_vm from ECM_host_blade server  ' + str(e))
        assert False



def take_corevm_config_backup(core_vm_2):
    try:
        log.info('Start Exporting open-am config file ')
        Report_file.add_line('Start Exporting open-am config file ')
        core_vm_ip, username, password = Server_details.core_vm_details(Server_details, core_vm_2=core_vm_2)
        log.info('Running for core_vm_ip ' + core_vm_ip)
        Report_file.add_line('Running for core_vm_ip ' + core_vm_ip)

        ShellHandler.__init__(ShellHandler, core_vm_ip, username, password)

        command = 'su - ecm_admin'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'cd /app/ecm/security/openAm/sso-tools/scripts ; ./export-config.sh'
        Report_file.add_line('Comamnd : ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler,command)
        command_output = str(stdout)
        Report_file.add_line('Comamnd Output : ' + command_output)
        if 'Service Configuration was exported' in command_output:
            log.info('Sucessfully Exported open-am config file')
            Report_file.add_line('Sucessfully Exported open-am config file')
        else:
            log.error('Somthing wrong Exporting open-am config file  , check output : '+command_output)
            Report_file.add_line('Somthing wrong Exporting open-am config file , check output : ' + command_output)
            assert False

        log.info('Start creating backup of  open-am config file - exported-openam-config.xml ')
        Report_file.add_line('Start creating backup of  open-am config file - exported-openam-config.xml ')

        file_name = Common_utilities.get_name_with_timestamp(Common_utilities,'exported-openam-config.xml' )
        log.info('Backup file name : '+file_name)
        Report_file.add_line('Backup file name : ' + file_name)
        command = 'mv  /app/ecm/security/openAm/exported-openam-config.xml /app/ecm/security/openAm/{}'.format(file_name)
        Report_file.add_line('Comamnd : ' + command)
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler,command)
        command_output = str(stdout)
        Report_file.add_line('Command Output : ' + command_output)


    except Exception as e:

        log.error('Error Exporting open-am config file ' + str(e))
        Report_file.add_line('Error Exporting open-am config file  ' + str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)

def check_jboss_server_status(core_vm_2):
    try:
        log.info('Start checking jboss serevr status ')
        Report_file.add_line('Start checking jboss serevr status ')
        core_vm_ip, username, password = Server_details.core_vm_details(Server_details,core_vm_2=core_vm_2)
        log.info('Running for core_vm_ip '+core_vm_ip)
        Report_file.add_line('Running for core_vm_ip ' + core_vm_ip)

        ShellHandler.__init__(ShellHandler, core_vm_ip, username, password)

        command = 'su - ecm_admin'
        stdin, stdout, stderr = ShellHandler.execute(ShellHandler, command)

        command = 'systemctl status jboss-eap | grep -i active'
        Report_file.add_line('Comamnd : ' + command)

        stdin, stdout, stderr = ShellHandler.execute(ShellHandler,command)
        command_output = str(stdout)
        Report_file.add_line('Comamnd Output : ' + command_output)

        if 'Active: active (running)' in command_output:
            log.info('Jboss server is up and running')
            Report_file.add_line('Jboss server is up and running')
        else:
            log.error('Jboss server is not up and running , check output : '+command_output)
            Report_file.add_line('Jboss server is not up and running , check output : ' + command_output)
            assert False
    except Exception as e:

        log.error('Error checking jboss serevr status ' + str(e))
        Report_file.add_line('Error checking jboss serevr status ' + str(e))
        assert False
    finally:
        ShellHandler.__del__(ShellHandler)

def update_ecm_session_count(core_vm_2):

        check_jboss_server_status(core_vm_2)

        take_corevm_config_backup(core_vm_2)

        place_updated_config_file_corevm(core_vm_2)

        import_updated_config_file_corevm(core_vm_2)

        time.sleep(5)

        check_jboss_server_status(core_vm_2)


def ecm_session_update():
    try:
        log.info('Start updating ECM session count using CORE-VM ')
        Report_file.add_line('Start updating ECM session count using CORE-VM ')
        deployment_type = Server_details.get_deployment_type(Server_details)

        if deployment_type == 'HA':
            update_ecm_session_count(core_vm_2=False)
            log.info('Running for second core_vm ip in HA env ')
            update_ecm_session_count(core_vm_2=True)
        else:
            update_ecm_session_count(core_vm_2=False)


        log.info('Finished updating ECM session count using CORE-VM ')
        Report_file.add_line('Finished updating ECM session count using CORE-VM ')
    except Exception as e:
        log.error( 'Error updating ECM session count using CORE-VM ' + str(e))
        Report_file.add_line('Error updating ECM session count using CORE-VM ' + str(e))
        assert False
