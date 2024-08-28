from behave import step
from com_ericsson_do_auto_integration_scripts.ECM_PACKAGE_DELETION import (start_terminating_ECM_packages_cn,
                                                                           start_terminating_ECM_packages)
from com_ericsson_do_auto_integration_model.Ecm_core import Ecm_core


@step("I start the Scenario to Delete all the packages from ECM Gui")
def step_impl(context):
    is_cloudnative = Ecm_core.get_is_cloudnative(Ecm_core)
    if is_cloudnative:
        start_terminating_ECM_packages_cn()
    else:
        start_terminating_ECM_packages()
