# pylint: disable=C0209.W0612,E0602,E0401
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
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_scripts.CEE_Cleanup import delete_stacks_from_cee
from com_ericsson_do_auto_integration_utilities.Server_details import Server_details
from com_ericsson_do_auto_integration_model.EPIS import EPIS

log = Logger.get_logger("OPENSTACK_STACK_CLEANUP.py")


def delete_stacks_from_openstack():
    try:
        project_name = EPIS.get_project_name(EPIS)
        openstack_ip, username, password, openrc_filename = \
            Server_details.openstack_host_server_details(Server_details)
        delete_stacks_from_cee(openrc_filename, project_name, openstack_ip, username, password, all_stack=True)
    except Exception as error:
        log.error("Exception while deleting stack ERROR: %s", str(error))
        assert False
