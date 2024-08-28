
from behave import step
from com_ericsson_do_auto_integration_scripts.CNF_NS_DEPLOYMENT import upload_tosca_cnf_package
from com_ericsson_do_auto_integration_model.SIT import SIT


@step("I start the Scenario to upload tosca cnf packages into Cloud Manager")
def step_impl(context):
    pkgs_dir_path = SIT.get_cnf_configmap_software_path(SIT)
    upload_tosca_cnf_package(pkgs_dir_path)
