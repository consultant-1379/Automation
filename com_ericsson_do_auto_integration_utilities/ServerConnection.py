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
Created on 20 Aug 2018

@author: emaidns
'''

import socket
import time
import paramiko
from scp import SCPClient

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.file_utils import MySFTPClient

log = Logger.get_logger('ServerConnection.py')


class ServerConnection(object):
    sshClient = paramiko.SSHClient()
    sshClient.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Removed as part of SM-101592
    # sshClient.load_system_host_keys()

    @staticmethod
    def get_file_sftp(connection, source, destination):
        try:
            log.info('Fetching source :  ' + source + ' to destination : ' + destination)
            sftp = connection.open_sftp()
            sftp.get(source, destination)
            sftp.close()
        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + source)
            assert False


    @staticmethod
    def put_file_sftp(connection, source, destination):
        try:
            log.info('Putting source :  ' + source + ' to destination : ' + destination)
            sftp = connection.open_sftp()
            sftp.put(source, destination)
            sftp.close()
        except Exception as e:
            log.error('Error: %s', str(e))
            assert False


    @staticmethod
    def put_folder_scp(connection, source, destination):

        try:
            log.info('Putting source :  ' + source + ' to destination : ' + destination)

            scp = SCPClient(connection.get_transport())

            scp.put(source, recursive=True, remote_path=destination)

            scp.close()

        except FileNotFoundError:
            log.error('File Not Found Error : Wrong file or file path : ' + source)
            assert False


    @staticmethod
    def get_nested_server_connection(local_connection,
                                     local_server_ip,
                                     dest_server_ip,
                                     dest_username,
                                     file_path):

        try:
            log.info('Getting nested connection with server :' + dest_server_ip)
            vmtransport = local_connection.get_transport()
            dest_addr = (dest_server_ip, 22)
            local_addr = (local_server_ip, 22)
            vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
            jhost = paramiko.SSHClient()
            jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # jhost.load_host_keys('/home/osmanl/.ssh/known_hosts')
            mykey = paramiko.RSAKey.from_private_key_file(file_path)
            jhost.connect(dest_server_ip, username=dest_username, pkey=mykey, sock=vmchannel)
            log.info('Connected with server :' + dest_server_ip)
            return jhost
        except paramiko.SSHException as e:

            log.warning("************* Login issue: SSH Exception ********************** ERROR :  " + str(e))
            log.info("Waiting 60 seconds to retry ")
            time.sleep(60)
            vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
            jhost = paramiko.SSHClient()
            jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            mykey = paramiko.RSAKey.from_private_key_file(file_path)
            jhost.connect(dest_server_ip, username=dest_username, pkey=mykey, sock=vmchannel)
            log.info('Connected with server :' + dest_server_ip)
            return jhost

        except paramiko.AuthenticationException as e:
            log.debug(e)
            log.error("Login issue: Please check the password, " + dest_server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False
        except (socket.error, paramiko.AuthenticationException) as e:
            log.debug(e)
            log.error("Connection refused with server :" + dest_server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False


    @staticmethod
    def make_nested_server_connection(localserver_ip,
                                      localserver_username,
                                      localserver_password,
                                      destinationserver_ip,
                                      destinationserver_username,
                                      destinationserver_password):
        """
        To make nested connection where both servers have password
        @param localserver_ip:
        @param localserver_username:
        @param localserver_password:
        @param destinationserver_ip:
        @param destinationserver_username:
        @param destinationserver_password:
        @return:
        """
        try:

            vm = paramiko.SSHClient()
            vm.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            log.info('Connecting to Blade server')
            vm.connect(localserver_ip, username=localserver_username, password=localserver_password)

            vmtransport = vm.get_transport()
            dest_addr = (destinationserver_ip, 22)
            local_addr = (localserver_ip, 22)
            vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)

            jhost = paramiko.SSHClient()
            jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            log.info('connecting to destination server from local server')
            jhost.connect(destinationserver_ip, username=destinationserver_username,
                          password=destinationserver_password, sock=vmchannel)

            log.info('Connected with server :' + destinationserver_ip)
            return jhost

        except paramiko.SSHException as e:
            log.warning("************* Login issue: SSH Exception ********************** ERROR :  " + str(e))
            log.info("Waiting 60 seconds to retry ")
            time.sleep(60)
            vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)

            jhost = paramiko.SSHClient()
            jhost.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            jhost.connect(destinationserver_ip, username=destinationserver_username,
                          password=destinationserver_password, sock=vmchannel)
            log.info('Connected with server :' + destinationserver_ip)
            return jhost
        except paramiko.AuthenticationException as e:
            log.debug(e)
            log.error("Login issue: Please check the password, " + destinationserver_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False
        except (socket.error, paramiko.AuthenticationException) as e:
            log.debug(e)
            log.error("Connection refused with server :" + destinationserver_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False


    @staticmethod
    def get_connection(server_ip, user_name, password):
        try:
            log.info('Connecting with server : %s', server_ip)
            ServerConnection.sshClient.connect(hostname=server_ip, username=user_name, password=password)
            log.info('Connected with server : %s', server_ip)
            return ServerConnection.sshClient
        except paramiko.SSHException as e:
            log.warning("************* Login issue: SSH Exception ********************** ERROR :  %s", str(e))
            log.info("Waiting 60 seconds to retry ")
            time.sleep(60)

            ServerConnection.sshClient.connect(hostname=server_ip, username=user_name, password=password)
            log.info('Connected with server : %s', server_ip)
            return ServerConnection.sshClient
        except paramiko.AuthenticationException as e:
            log.debug(e)
            log.error("Login issue: Please check the password, %s", server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False
        except (socket.error, paramiko.AuthenticationException) as e:
            log.debug(e)
            log.error("Connection refused with server : %s ", server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False


    @staticmethod
    def get_connection_with_file(server_ip, user_name, file_path):

        try:
            log.info('Connecting with server :' + server_ip)
            sshClient1 = paramiko.SSHClient()
            sshClient1.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # sshClient1.load_system_host_keys()
            mykey = paramiko.RSAKey.from_private_key_file(file_path)
            sshClient1.connect(hostname=server_ip, username=user_name, pkey=mykey)
            log.info('Connected with server :' + server_ip)
            return sshClient1
        except paramiko.SSHException as e:
            log.warning("************* Login issue: SSH Exception ********************** ERROR :  " + str(e))
            log.info("Waiting 60 seconds to retry ")
            time.sleep(60)

            sshClient1.connect(hostname=server_ip, username=user_name, pkey=mykey)
            log.info('Connected with server :' + server_ip)
            return sshClient1
        except paramiko.AuthenticationException as e:
            log.error("Login issue: Please check the password, " + server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False
        except (socket.error, paramiko.AuthenticationException) as e:
            log.error("Connection refused with server :" + server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False


    @staticmethod
    def get_thread_connection(server_ip, user_name, password):

        try:
            log.info('Connecting with server :' + server_ip)
            sshClient_thread = paramiko.SSHClient()
            sshClient_thread.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            # sshClient_thread.load_system_host_keys()
            sshClient_thread.connect(hostname=server_ip, username=user_name, password=password)
            log.info('Connected with server :' + server_ip)
            return sshClient_thread
        except paramiko.SSHException as e:
            log.warning("************* Login issue: SSH Exception ********************** ERROR :  " + str(e))
            log.info("Waiting 60 seconds to retry ")
            time.sleep(60)

            sshClient_thread.connect(hostname=server_ip, username=user_name, password=password)
            log.info('Connected with server :' + server_ip)
            return sshClient_thread
        except paramiko.AuthenticationException as e:
            log.debug(e)
            log.error("Login issue: Please check the password, " + server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False
        except (socket.error, paramiko.AuthenticationException) as e:
            log.debug(e)
            log.error("Connection refused with server :" + server_ip)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            assert False


    def close(self):
        log.info('Connection closed with server ')
        self.sshClient.close()


    @staticmethod
    def check_Server_Error(connection):
        command = 'sudo -i ls -lrt'
        stdin, stdout, stderr = connection.exec_command(command)
        command_error = stderr.read().decode("utf-8")

        if command_error:
            log.error(command_error)
            Report_file.add_line(command_error)
            log.info('''Replace "Defaults requiretty" by \n"#Defaults requiretty" in\n"/etc/sudoers" file''')
            Report_file.add_line('''Replace "Defaults requiretty" by \n"#Defaults requiretty" in\n"/etc/sudoers" file''')
            connection.close()
            return True
        else:
            log.info('command success for sudo ..')
            connection.close()
            return False

    @staticmethod
    def file_exists(host, username, password, sftpPath):
        port = 22
        sftpTransport = paramiko.Transport((host, port))
        sftpTransport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(sftpTransport)
        try:
            sftp.stat(sftpPath)
            log.info('File present at path ' + sftpPath)
            sftp.close()
            sftpTransport.close()
            return True;

        except:
            log.info('File not present, creating file ' + sftpPath)
            sftp.close()
            sftpTransport.close()
            return False


    @staticmethod
    def transfer_folder_local_to_remote(host, username, password, source_path, target_path):

        log.info('Putting source :  ' + source_path + ' to destination : ' + target_path)
        port = 22
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)

        sftp = MySFTPClient.from_transport(transport)
        log.info('starting to transfer dir ' + source_path)
        # sftp.mkdir(target_path, ignore_existing=True)
        sftp.put_dir(source_path, target_path)
        sftp.close()


    @staticmethod
    def transfer_files_using_scp(connection, serverip, username, password, dest_path, source_path):
        """
        This Method is used to transfer files between two servers(server to server)
        @param connection:
        @param serverip:
        @param username:
        @param password:
        @param dest_path:
        @param source_path:
        """
        try:
            log.info(f'Transfer file/folder {source_path} to {serverip} at path {dest_path}')
            Report_file.add_line(f'Transfer file/folder {source_path} to {serverip} at path {dest_path}')
            # command to clear the ip from ssh_host file
            remove_ip = 'ssh-keygen -R {}'.format(serverip)
            connection.exec_command(remove_ip)

            interact = connection.invoke_shell()
            destination = username + '@' + serverip
            command = 'scp -r -p ' + source_path + ' ' + destination + ':' + dest_path + ''
            log.info("Command To Transfer file - " + command)
            Report_file.add_line("Command To Transfer file - " + command)
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
                interact.send(password + '\n')

                log.info('Waiting 50 seconds to transfer ')
            time.sleep(50)
            log.info(f'Complete transfer file/folder {source_path} to {serverip} at path {dest_path}')
            Report_file.add_line(f'Complete transfer file/folder {source_path} to {serverip} at path {dest_path}')
        except Exception as e:
            log.error('Error while transferring ' + source_path + ' file ' + str(e))
            Report_file.add_line('Error while transferring ' + source_path + ' file ' + str(e))
            assert False


    @staticmethod
    def transfer_files_with_an_encrypted_pem_file(connection, private_key_file,
                                                  source_path, username, server_ip,
                                                  destination_path):
        """this method used to transfer file and folder both from one server to other server"""
        try:
            log.info('Start to transfer the file' + source_path)
            Report_file.add_line('Start to transfer the file' + source_path)

            command = ('scp '
                       '-o UserKnownHostsFile=/dev/null '
                       '-o StrictHostKeyChecking=no '
                       '-i {} -r {} {}@{}:{}'.format(private_key_file,
                                                         source_path,
                                                         username,
                                                         server_ip,
                                                         destination_path))

            stdin, stdout, stderr = connection.exec_command(command)
            log.info("Command to Transfer file : " + command)
            Report_file.add_line("Command to Transfer file : " + command)
            command_output = str(stdout.read())
            Report_file.add_line('command output - ' + command_output)
            ret_out = stdout.channel.recv_exit_status()
            log.info('RC: %s', ret_out)
            if ret_out == 0:
                log.info('successfully transferred the file' + source_path)
                Report_file.add_line('successfully transferred the file' + source_path)

            else:
                log.info('Failed to  transferred the file' + source_path)
                Report_file.add_line('Failed to transferred the file' + source_path)
                assert False

        except Exception as e:

            log.info('Error while transferring file ' + str(e))
            Report_file.add_line('Error while transferring file ' + str(e))
            assert False


    @staticmethod
    def transfer_files_with_user_and_passwd(connection, username, password, source_path, server_ip,
                                            destination_path):
        try:

            log.info('Start to transfer the file' + source_path)
            Report_file.add_line('Start to transfer the file' + source_path)

            command = '''curl --insecure --user {}:{} -T {} sftp://{}{}'''.format(username,
                                                                                  password,
                                                                                  source_path,
                                                                                  server_ip,
                                                                                  destination_path)
            log.info("Command to Transfer file : " + command)
            Report_file.add_line('Command to transfer file ' + command)

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('command output - ' + command_output)
            ret_out = stdout.channel.recv_exit_status()

            if ret_out == 0:
                log.info('successfully transferred the file' + source_path)
                Report_file.add_line('successfully transferred the file' + source_path)

            else:
                log.info('Failed to  transferred the file' + source_path)
                Report_file.add_line('Failed to transferred the file' + source_path)
                assert False

        except Exception as e:

            log.info('Error While transferring the file ' + str(e))
            Report_file.add_line('Error while transferring the file' + str(e))
            assert False


    @staticmethod
    def transfer_folder_with_user_and_passwd(connection, username, password, source_path, server_ip,
                                             destination_path):
        try:

            log.info('Start to transfer the file' + source_path)
            Report_file.add_line('Start to transfer the file' + source_path)

            command = '''curl --insecure --user {}:{} -T {} sftp://{}{}'''.format(username,
                                                                                  password,
                                                                                  source_path,
                                                                                  server_ip,
                                                                                  destination_path)
            log.info("Command to Transfer file : " + command)
            Report_file.add_line('Command to transfer file ' + command)

            stdin, stdout, stderr = connection.exec_command(command)
            command_output = str(stdout.read())
            Report_file.add_line('command output - ' + command_output)
            ret_out = stdout.channel.recv_exit_status()

            if ret_out == 0:
                log.info('successfully transferred the file' + source_path)
                Report_file.add_line('successfully transferred the file' + source_path)

            else:
                log.info('Failed to  transferred the file' + source_path)
                Report_file.add_line('Failed to transferred the file' + source_path)
                assert False

        except Exception as e:

            log.info('Error While transferring the file ' + str(e))
            Report_file.add_line('Error while transferring the file' + str(e))
            assert False


    @staticmethod
    def delete_copyfile(connection, file_name):
        Report_file.add_line('Start to delete ' + file_name + ' file.')
        rm_file_cmd = 'rm -rf ' + file_name
        Report_file.add_line('Command - ' + rm_file_cmd)
        stdin, stdout, stderr = connection.exec_command(rm_file_cmd)
        command_output = str(stdout.read())
        Report_file.add_line('command_output - ' + command_output)


    @staticmethod
    def transfer_folder_between_remote_servers(connection, ip, username, password, src, dest, filepath, option):
        """
        Used to transfer the files/folder between two remote servers
        Connection : source server connection with local from where file/folder need to be transfered
        ip : destination server ip 
        username : destination username
        password : destination password
        src example : /var/tmp/deployEPG3.7_VM_VNFM/epg_3.7
        dest example : /vnflcm-ext/current/vnf_package_repo/
        filepath : path on source server for copyfiles.sh
        @param connection:
        @param ip:
        @param username:
        @param password:
        @param src:
        @param dest:
        @param filepath:
        @param option:

        """
        try:
            log.info('Start to transfer ' + str(src) + ' to ' + ip)
            Report_file.add_line('Start to transfer ' + str(src) + ' to ' + ip)
            file_name = 'copyfiles.sh'

            copyfilepath = filepath + file_name

            sftp = connection.open_sftp()
            sftp.put(r'com_ericsson_do_auto_integration_files/' + file_name, copyfilepath)
            sftp.close()

            per_cmd = 'cd ' + filepath + ' ; chmod 777 ' + file_name
            Report_file.add_line('File permission Command ' + per_cmd)
            stdin, stdout, stderr = connection.exec_command(per_cmd)
            command_output = str(stdout.read())
            # Changing file mode from windows to unix
            cmd = f'''cd {filepath} ; sed -i 's/\r//' {file_name}'''
            Report_file.add_line('Command - ' + cmd)
            stdin, stdout, stderr = connection.exec_command(cmd)
            command_output = str(stdout.read())

            if option == 'put':
                # Here src is file which needs to be copy
                # dest is where to copy on the another server
                cmd_to_run = 'scp -p \
                                    -o UserKnownHostsFile=/dev/null \
                                    -o StrictHostKeyChecking=no \
                                    -r {} {}@{}:{}'.format(src, username, ip, dest)
            else:
                # Here src is which file need to copy from another server
                # dest is where to copy on the server
                cmd_to_run = 'scp -p \
                                    -o UserKnownHostsFile=/dev/null \
                                    -o StrictHostKeyChecking=no \
                                    -r {}@{}:{} {}'.format(username, ip, dest, src)

            cmd_to_run = '"' + cmd_to_run + '"'
            Report_file.add_line('SCP Command  - ' + cmd_to_run)

            cmd = './{} {} {}'.format(file_name, password, cmd_to_run)
            Report_file.add_line('Command to run copyfiles.sh file  - ' + cmd)
            log.info("Transferring the file. Please wait...")
            stdin, stdout, stderr = connection.exec_command(cmd)
            command_output = str(stdout.read())
            output = command_output[-4:]
            output = output.split('\\n')[0]

            log.info('Command output - ' + command_output)
            Report_file.add_line('Command output - ' + command_output)

            if '100%' in command_output:
                log.info('File transferred ' + str(src) + ' Successfully.' + ip)
                Report_file.add_line('File transferred ' + str(src) + ' Successfully.' + ip)
                ServerConnection.delete_copyfile(connection, file_name)
            else:

                log.info('Failed to transfer ' + str(src) + ' file to  ' + ip)
                Report_file.add_line('Failed to transfer ' + str(src) + ' file to  ' + ip)
                ServerConnection.delete_copyfile(connection, file_name)
                assert False

        except Exception as e:

            log.info('Error While transferring the file ' + str(e))
            Report_file.add_line('Error while transferring the file' + str(e))
            assert False
