from behave import step

from com_ericsson_do_auto_integration_files.MONITOR_RESOURCES_DEPLOYED.config import RESOURCE_TYPES
from com_ericsson_do_auto_integration_scripts.MONITOR_UNAPPROVED_RESOURCES_DEPLOYED import ResourceMonitor

RESOURCE_MONITOR_INSTANCE = ResourceMonitor()


@step("I start the Scenario to collect resources deployed")
def step_impl(context):
    context.monitor = RESOURCE_MONITOR_INSTANCE
    for resource_type in RESOURCE_TYPES:
        context.monitor.collect_resources_deployed(resource_type)


@step("I start the Scenario to collect details of resources")
def step_impl(context):
    context.monitor = RESOURCE_MONITOR_INSTANCE
    context.monitor.collect_details_of_resources()


@step("I start the Scenario to check_for_unapproved_resources_details")
def step_impl(context):
    context.monitor.check_for_unapproved_resources_details()
