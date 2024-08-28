from behave import *
from com_ericsson_do_auto_integration_scripts.METRICS_TESTS import *


@step("I start the Scenario to Collect Codeploy Metrics Tests")
def step_impl(context):
    collect_metrics_tests()





