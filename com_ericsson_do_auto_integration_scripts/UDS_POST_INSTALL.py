# ********************************************************************
# Ericsson LMI                                    SCRIPT
# ********************************************************************
#
# (c) Ericsson LMI 2021
#
# The copyright to the computer program(s) herein is the property of
# Ericsson LMI. The programs may be used and/or copied only  with the
# written permission from Ericsson LMI or in accordance with the terms
# and conditions stipulated in the agreement/contract under  which the
# program(s) have been supplied.
#
# ********************************************************************
'''
Created on 21 Jan 2021

@author: zsyapra
'''
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import *

log = Logger.get_logger('UDS_POST_INSTALL.py')


class UDC_POST_INST:

    def take_backup_of_uds(self):
        filename = 'snapshotCassandra.sh'
        self.run_script_on_uds_pod(self,filename,'back_up')

    def cleanup_data_on_uds(self):
        filename = 'restoreCassandra.sh'
        self.run_script_on_uds_pod(self, filename, 'clean_up')




    def run_script_on_uds_pod(self,filename,action):
        try:
            log.info(f'Start {action} of UDS')
            Report_file.add_line(f'Start {action} of UDS')

            ecm_server_ip, ecm_username, ecm_password = Server_details.ecm_host_blade_details(Server_details)

            vm_vnfm_director_ip, vm_vnfm_director_username = Server_details.vm_vnfm_director_details(Server_details)

            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

            connection = ServerConnection.get_connection(ecm_server_ip, ecm_username, ecm_password)


            if vm_vnfm_namespace == 'codeploy':

                #ServerConnection.put_file_sftp(connection, 'id_rsa_tf.pem', '/root/id_rsa_tf.pem')
                file_path = 'id_rsa_tf.pem'

            else:
                #ServerConnection.put_file_sftp(connection, 'eccd-2-3.pem', '/root/eccd-2-3.pem')
                file_path = 'eccd-2-3.pem'

            destination_filepath = '/home/' + vm_vnfm_director_username + "/"

            source_filepath = SIT.get_base_folder(SIT) + filename

            # Transferring file from local to blade server
            ServerConnection.put_file_sftp(connection,
                                            r'com_ericsson_do_auto_integration_files/UDS_files/' + filename,
                                            SIT.get_base_folder(SIT) + filename)

            # Transferring file from blade server to vm vnfm
            ServerConnection.transfer_files_with_an_encrypted_pem_file(connection, file_path,
                                                                       source_filepath, vm_vnfm_director_username,
                                                                       vm_vnfm_director_ip, destination_filepath)

            connection.close()

            dir_connection = get_VMVNFM_host_connection()

            source = '/home/eccd/'+filename

            filepath = '/tmp/'

            pod = 'eric-data-wide-column-database-cd-0'

            transfer_file_to_pod_db(pod, vm_vnfm_namespace, dir_connection, source, filepath)

            change_file_permissions_of_file_on_pod_db(pod, vm_vnfm_namespace, dir_connection, filename, filepath)

            command = 'kubectl -n {} exec -it {} -- bash -c  "cd {};bash {}"'.format(vm_vnfm_namespace, pod, filepath,
                                                                                     filename)

            Report_file.add_line('command : ' + command)

            stdin, stdout, stderr = dir_connection.exec_command(command)

            command_output = str(stdout.read())

            log.info(command_output)

            Report_file.add_line('command_output : ' + command_output)

            if 'afterDeploy' in command_output and filename == 'snapshotCassandra.sh':
                log.info('Back up has been taken successfully.')
                Report_file.add_line('Back up has been taken successfully.')
            elif 'restore completed successfully' in command_output and filename =='restoreCassandra.sh':
                log.info('Cleanup on UDS is successfully completed .')
                Report_file.add_line('Cleanup on UDS is successfully completed .')
            else:
                log.info(f'Failed {action} action on uds, please check command output for more details..')
                Report_file.add_line(f'Failed {action} action on uds, please check command output for more details..')
                assert False

        except Exception as e:
            log.error(f'Error while {action} of uds' + str(e))
            Report_file.add_line(f'Error while {action} of uds' + str(e))
            assert False

        finally:

            dir_connection.close()


    def restart_uds_service_pod(self):

        try:
            log.info('Start fetching out the id for uds service pod ')
            Report_file.add_line('Start fetching out the id for uds service pod ')

            ecm_host_data = Initialization_script.get_model_objects(Initialization_script, 'ECM_CORE')

            vm_vnfm_namespace = ecm_host_data._Ecm_core__vm_vnfm_namespace

            dir_connection = get_VMVNFM_host_connection()

            command = f"kubectl get pods --namespace {vm_vnfm_namespace} | grep -P 'eric-oss-uds-service-(?!config)[a-z0-9]+(-)*[a-z0-9]*'"

            Report_file.add_line('command : ' + command)

            stdin, stdout, stderr = dir_connection.exec_command(command)
            command_out = str(stdout.read())

            Report_file.add_line('command output: ' + command_out)
            command_output = command_out[2:-1:1].split()

            pod_id = command_output[0].strip()
            pod_status = command_output[2].strip()

            log.info(f'Id  uds service pod is {pod_id} and status is {pod_status}')
            Report_file.add_line(f'Id  uds service pod is {pod_id} and status is {pod_status}')


            log.info('Going to delete the POD to restart it')

            command  = f"kubectl delete pods -n {vm_vnfm_namespace} {pod_id}"

            Report_file.add_line('command : ' + command)

            stdin, stdout, stderr = dir_connection.exec_command(command)

            command_out = str(stdout.read())

            Report_file.add_line('command_output : ' + command_out)

            log.info('waiting 75 seconds to terminate the pod ')
            time.sleep(75)

            time_out = 1200

            log.info('checking for uds service pod initialization status')
            log.info('time out for this process is 1200 seconds')

            command = f"kubectl get pods --namespace {vm_vnfm_namespace} | grep -P 'eric-oss-uds-service-(?!config)[a-z0-9]+(-)*[a-z0-9]*'"
            Report_file.add_line('command : ' + command)
            while (time_out != 0):


                stdin, stdout, stderr = dir_connection.exec_command(command)

                command_out = str(stdout.read())

                Report_file.add_line('command output: ' + command_out)
                command_output = command_out[2:-1:1].split()

                pod_id = command_output[0].strip()
                pod_status = command_output[2].strip()

                if 'Running' == pod_status:
                    log.info(f'POD status is running and new id is {pod_id}')
                    Report_file.add_line(f'POD status is running and new id is {pod_id}')
                    break

                else:
                    log.info(f'POD status is {pod_status}')
                    Report_file.add_line(f'POD status is {pod_status}')
                    log.info('waiting for 30 seconds to check again')
                    time_out = time_out - 30
                    time.sleep(30)

            if time_out ==0:
                log.error('Timed out while fetching POD status , please check status in logs ')
                Report_file.add_line('Timed out while fetching POD status , please check status in logs ')
                assert False

            log.info('waiting 10 seconds to check container ready status')

            time.sleep(10)

            time_out = 600

            log.info('Going to check container ready status')
            Report_file.add_line('Going to check container ready status')
            log.info('Time out for this process is 600 seconds')

            command = f"kubectl get pod -n {vm_vnfm_namespace} {pod_id} -o custom-columns=POD:metadata.name,READY:status.containerStatuses[*].ready | grep -i {pod_id}"

            Report_file.add_line('command : ' + command)
            while (time_out != 0):

                stdin, stdout, stderr = dir_connection.exec_command(command)
                command_out = str(stdout.read())

                Report_file.add_line('command output: ' + command_out)

                command_output = command_out[2:-3:1].split()

                if 'true' == command_output[1]:
                    log.info('UDS service pod is up and running .. , Usecase succesful')
                    Report_file.add_line('UDS service pod is up and running .. , Usecase succesful')
                    break
                elif 'false' == command_output[1]:
                    log.info(f'POD container {pod_id} status is {command_output[1]}')
                    Report_file.add_line(f'POD container {pod_id} status is {command_output[1]}')
                    log.info('Waiting for 30 seconds to check again if POD is running')
                    time_out = time_out - 30
                    time.sleep(30)
                else:
                    log.error('Something wrong with pod container , please check command output ')
                    Report_file.add_line('Something wrong with pod container , please check command output ')
                    assert False

            if time_out ==0:
                log.error(f'Timed out while fetching POD container {pod_id} status')
                Report_file.add_line(f'Timed out while fetching POD container {pod_id} status')
                assert False

        except Exception as e:
            log.error(f'Error while checking uds pod service ' + str(e))
            Report_file.add_line(f'Error while checking uds pod service' + str(e))
            assert False

        finally:

            dir_connection.close()




    def verify_uds_restore_database_status(self, command, director_connection):
        Report_file.add_line('Command - ' + command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())
        Report_file.add_line('Command Output : ' + command_output)
        if 'deleted' in command_output:
            log.info('Restoring the database completed successfully.')
            Report_file.add_line('Restoring the database completed successfullysss .')
        else:
            log.info(f'Failed restoring the database on uds, please check command output for more details..')
            Report_file.add_line(f'Failed restoring the database on uds, please check command output for more details..')
            assert False


    def delete_and_restart_pods(self):
        try:
            log.info('Start to delete pod and go into Pod Initializing and restart the Service pod.')
            Report_file.add_line('Start to delete pod and go into Pod Initializing and restart the pod.')
            vm_vnfm_namespace = Server_details.get_vm_vnfm_namespace(Server_details)

            director_connection = get_VMVNFM_host_connection()

            command = f'''kubectl get job -n {vm_vnfm_namespace} eric-oss-uds-service-config-cassandra-job -o json | jq 'del(.spec.selector)' | jq 'del(.spec.template.metadata.labels)' | kubectl replace --force -f - 2>&1 '''
            self.verify_uds_restore_database_status(self, command, director_connection)
            command1 = f''' kubectl get job -n {vm_vnfm_namespace} eric-oss-uds-onboarding-service-job -o json | jq 'del(.spec.selector)' | jq 'del(.spec.template.metadata.labels)' | kubectl replace --force -f -   2>&1'''
            self.verify_uds_restore_database_status(self, command1, director_connection)
            command2 = f'''kubectl get job -n {vm_vnfm_namespace} eric-oss-uds-service-config-backend-job -o json | jq 'del(.spec.selector)' | jq 'del(.spec.template.metadata.labels)' | kubectl replace --force -f -  2>&1'''
            self.verify_uds_restore_database_status(self,command2, director_connection)

        finally:
            director_connection.close()
