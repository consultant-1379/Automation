from behave import step
from com_ericsson_do_auto_integration_scripts.SO_CNF_CONFIGMAP_PRE_REQ import CnfConfigmapPreReq as cnf_pre_req


@step("I start the Scenario to Upload etsi tosca vnfd packages")
def step_impl(context):
    cnf_pre_req.upload_cnfd_packages(cnf_pre_req)


