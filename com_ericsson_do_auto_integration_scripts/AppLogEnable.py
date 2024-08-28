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

from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.ServerConnection import ServerConnection
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection, get_vmvnfm_pod_cmd
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core

log = Logger.get_logger('AppLogEnable.py')


class AppLogEnable:
    """
    Enable/Disable debug logs
    """

    @staticmethod
    def vnflcm_vmvnfm_log_enable_disable_commands(action):
        # Commands must be in same order of execution
        if action == 'enable':
            enable_command_list = [
                "/ericsson/3pp/jboss/bin/jboss-cli.sh -c --command='/subsystem=logging/root-logger=ROOT:write-attribute(name=level,value=INFO)'",
                "/ericsson/3pp/jboss/bin/jboss-cli.sh -c --command='/subsystem=logging/logger=com.ericsson.oss.services.vnflaf:write-attribute(name=level,value=DEBUG)'",
                "/ericsson/3pp/jboss/bin/jboss-cli.sh -c --command='/subsystem=logging/logger=com.ericsson.oss.services.vnflcm:write-attribute(name=level,value=DEBUG)'"
            ]
            return enable_command_list
        if action == 'disable':
            disable_command_list = [
                "/ericsson/3pp/jboss/bin/jboss-cli.sh -c --command='/subsystem=logging/logger=com.ericsson.oss.services.vnflaf:write-attribute(name=level,value=INFO)'",
                "/ericsson/3pp/jboss/bin/jboss-cli.sh -c --command='/subsystem=logging/logger=com.ericsson.oss.services.vnflcm:write-attribute(name=level,value=INFO)'"
            ]
            return disable_command_list

    def trigger_vmvnfm_vnflcm_commands(self, action):
        """
        Trigger vm-vnfm commands to enable/disable logs
        """
        dir_connection = None
        try:
            log.info('Start %s the debug logs for vm-vnfm', action)
            Report_file.add_line(f'Start {action} the debug logs for vm-vnfm')

            vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)
            lcm_server_ip, lcm_username, lcm_password = Server_details.lcm_host_server_details(Server_details)
            is_vm_vnfm = Server_details.is_vm_vnfm_usecase(Server_details)

            if is_vm_vnfm == 'TRUE':
                dir_connection = get_VMVNFM_host_connection()
            else:
                dir_connection = ServerConnection.get_connection(lcm_server_ip, lcm_username, lcm_password)

            command_list = self.vnflcm_vmvnfm_log_enable_disable_commands(action)
            for command in command_list:
                if is_vm_vnfm == 'TRUE':
                    kubctl_command = get_vmvnfm_pod_cmd(command)
                else:
                    kubctl_command = command

                log.info('command: %s', kubctl_command)
                stdin, stdout, stderr = dir_connection.exec_command(kubctl_command)

                command_output = str(stdout.read())
                log.info('output: %s', command_output)

                if 'success' in command_output:
                    log.info('Command is successful to %s the debug logs', action)

                elif 'failed' in command_output:
                    log.error('Command has failed to %s the debug logs, please check the above output', action)
                    assert False
                else:
                    log.info('Failed %s action on vm vnfm, please check command output for more details', action)
                    assert False

        except Exception as error:
            log.error('Error while %s the debug logs on vmvnfm: %s', action, str(error))
            assert False

        finally:
            dir_connection.close()

    def start_enable_debug_logs(self):
        self.trigger_vmvnfm_vnflcm_commands(self, 'enable')

    def start_disable_debug_logs(self):
        self.trigger_vmvnfm_vnflcm_commands(self, 'disable')
