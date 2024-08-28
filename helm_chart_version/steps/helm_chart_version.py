from com_ericsson_do_auto_integration_scripts.HELM_CHART_VERSION import get_helm_chart_version
from behave import step


@step("I start the Scenario to Check the helm chart version for given name")
def step_impl(context):
    get_helm_chart_version()
