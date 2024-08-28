from behave import step

from com_ericsson_do_auto_integration_scripts.VERIFY_NODE_DEPLOYMENT import enm_tosca_node_cleanup, \
    enm_etsi_tosca_node_cleanup
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('enm_node_cleanup_impl.py')


@step("I start the Scenario to cleanup tosca node in enm")
def step_impl(context):
    enm_tosca_node_cleanup()


@step("I start the Scenario to cleanup etsi tosca node in enm")
def step_impl(context):
    enm_etsi_tosca_node_cleanup()
