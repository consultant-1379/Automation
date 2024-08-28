"""
Created on Feb 22, 2022
@author: zkotkot
"""

import re
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_initilization.SIT_initialization import Initialization_script
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core

log = Logger.get_logger('EAI_ND_SUPERUSER_CREATION.py')

def create_eai_nd_superuser():

    """This method is used to create eai nd superuser"""

    try:
        log.info('start creating eai nd super user')
        Report_file.add_line('start creating eai nd super user')

        director_connection = get_VMVNFM_host_connection()
        vm_vnfm_namespace = Ecm_core.get_vm_vnfm_namespace(Ecm_core)

        # Executing kubectl command to fetch the active pod name
        command = f'kubectl get pod -n {vm_vnfm_namespace}|grep eric-eo-engine'
        log.info('Executing Command - %s', command)
        Report_file.add_line('Executing Command -'+ command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info('Command output- %s', command_output)

        # Getting the engine and pod names from command_output
        new_engine_name = re.search(r'(eric-eo-engine-)\s*(\w+\-\w+)',command_output).group()
        log.info('engine_name - %s', new_engine_name)

        # Replacing the old pod name with new pod value in CreateSuperUser.sh file
        command = f"sed -i 's/eric-eo-engine-[0-9a-z\-]*/{new_engine_name}/g' CreateSuperUser.sh"
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())
        log.info('Command output- %s', command_output)

        # Executing ./CreateSuperUser.sh file to create the super user
        command = './CreateSuperUser.sh'
        log.info('Executing Command - %s', command)
        Report_file.add_line('Executing Command - '+ command)
        stdin, stdout, stderr = director_connection.exec_command(command)
        command_output = str(stdout.read())

        log.info('Command Output - %s', command_output)
        Report_file.add_line('Command Output -'+ command_output)

        # Verification of success message after executing ./CreateSuperUser.sh file
        message = 'HTTP/1.1 200 OK'
        if message in command_output:
            log.info('eai nd super user has been created')
            Report_file.add_line('eai nd super user has been created')
        else:
            log.info('eai nd super user was not created')
            Report_file.add_line('eai nd super user was not created')
            assert False

    except Exception as error:

        log.info('Error while creating eai nd super user %s', str(error))
        Report_file.add_line('Error while creating eai nd super user'+ str(error))
        assert False
