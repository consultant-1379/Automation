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
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_files.NS_PDB_MONITOR.config import *

log = Logger.get_logger('NS_PDB_MONITOR.py')


def check_ns_pdb_value():
    """
    We have vnf_type attribute , that is used to take inputs from jenkins job .
    do not get confuse with vnf type , here we are using it for user input
    namespace from jenkins job
    """
    conn = None
    try:
        # jenkins parameter namespace
        namespace = SIT.get_vnf_type(SIT)
        log.info('Start checking pdb value for namespace :: %s', namespace)

        conn = get_VMVNFM_host_connection(SIT.get_is_ccd(SIT))

        output = get_pdb_value(conn, namespace)

        if output:
            log.error("PDB found with ALLOWED DISRUPTION value zero")
            print_output(output)
            assert False
        else:
            log.info("No PDB found with ALLOWED DISRUPTION value zero")

        log.info('Finished checking NS pdb value')
    except Exception as e:
        log.error('Error while checking NS pdb value: %s', str(e))
        assert False

    finally:
        if conn:
            conn.close()


def get_pdb_value(conn, namespace):
    """
    This method will return pdb names if any of them contains allowed_disruption value zero
    job will fail if any pdb found with allowed_disruption = 0
    """
    try:
        cmd = f"kubectl get pdb -n {namespace} -o custom-columns='NAME':.metadata.name,'ALLOWED " \
              f"DISRUPTIONS':.status.disruptionsAllowed |awk '{awk_cmd}' "

        log.info("command : %s", cmd)

        stdin, stdout, stderr = conn.exec_command(cmd)
        handle_stderr(stderr, log)

        output = stdout.read().decode("utf-8")

        log.info("command output : %s", output)

        return output
    except Exception as e:
        log.error('Error while looking for pdb value: %s', str(e))
        assert False


def print_output(output):
    print('=' * 105)
    print("\nPDB NAMES WITH ALLOWED DISRUPTION VALUE ZERO(0)\n")
    print('=' * 105)
    print(output)
    print('=' * 105)
