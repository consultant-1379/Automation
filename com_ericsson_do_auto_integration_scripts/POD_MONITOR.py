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

from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_files.POD_MONITOR.config import *

log = Logger.get_logger('POD_MONITOR.py')


def check_pod_status():

    try:
        log.info('Start checking POD restarts')

        conn = get_VMVNFM_host_connection(SIT.get_is_ccd(SIT))
        namespace = SIT.get_vnf_type(SIT)

        get_rogue_pods(conn, namespace)

        log.info('Finished checking POD restarts')
    except Exception as e:
        log.error('Error while checking POD restarts: %s', str(e))
        assert False


def get_rogue_pods(conn, namespace):

    try:
        cmd = f"{k8s_get_pod} {namespace} |awk '{awk_cmd}'"

        stdin, stdout, stderr = conn.exec_command(cmd)
        out = stdout.read().decode('utf-8')

        if len(out) > 150:
            print_output(out)
            log.error('Found PODs with restarts or status other then RUNNING.')
            assert False
        log.info('No PODs with restarts found.')

    except Exception as e:
        log.error('Error while looking for suspicious pods: %s', str(e))
        assert False


def print_output(out):
    print('\n' * 2)
    print('PODs WITH RESTARTS OR FAULTS')
    print('=' * 105)
    print(out)
    print('=' * 105)
    print('\n' * 2)
