
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
"""
Error handling module
"""
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file


def handle_stderr(stderr, log):
    """
    Handles stderr from shell
    stderr - standard error from shell executor
    log - logger we pass to function
    """
    error_output = stderr.read().decode("utf-8")
    if error_output:
        if 'you are not an authorized user' in error_output:
            pass
        else:
            log.error("Error message :" + error_output)
            assert False
