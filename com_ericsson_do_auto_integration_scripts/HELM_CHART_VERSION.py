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

from com_ericsson_do_auto_integration_model.SIT import SIT
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.file_utils import create_property_file
from com_ericsson_do_auto_integration_scripts.VM_VNFM_OPERATIONS import get_VMVNFM_host_connection

log = Logger.get_logger('HELM_CHART_VERSION.py')


def get_helm_chart_version():
    """
    We have vnf_type attribute , that is used to take inputs from jenkins job .
    do not get confuse with vnf type , here we are using it for user input
    Helm name  from jenkins job
    """
    conn = None
    try:
        # jenkins parameter HELM_NAME
        helm_name = SIT.get_vnf_type(SIT)
        log.info('Start checking helm chart version for name :: %s', helm_name)

        conn = get_VMVNFM_host_connection(SIT.get_is_ccd(SIT))

        output = get_helm_chart(conn, helm_name)

        # separate name and version from output
        replace_str = helm_name + "-"
        version = output.replace(replace_str, "")

        # create property file for use of EO-staging
        create_property_file("artifacts.properties", helm_name, version)
        print_output(output)

        log.info('Finished getting helm chart version task')
    except Exception as e:
        log.error('Error while getting helm chart version: %s', str(e))
        assert False

    finally:
        if conn:
            conn.close()


def get_helm_chart(conn, helm_name):
    """
    This method will return chart attribute value
    """
    try:
        print_option = "{print $9}"
        helm_name = f'"{helm_name}"'
        cmd = f"helm ls -A | awk '$1=={helm_name} {print_option}'"

        log.info("command : %s", cmd)

        stdin, stdout, stderr = conn.exec_command(cmd)
        handle_stderr(stderr, log)

        output = stdout.read().decode("utf-8")

        log.info("command output : %s", output)

        return output
    except Exception as e:
        log.error('Error while getting chart version: %s', str(e))
        assert False


def print_output(output):
    print('=' * 105)
    print("\nHELM CHART VERSION\n")
    print('=' * 105)
    print(output)
    print('=' * 105)
