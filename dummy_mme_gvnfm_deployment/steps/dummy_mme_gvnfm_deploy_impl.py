
from behave import *
from com_ericsson_do_auto_integration_scripts.DUMMY_MME_GVNFM_DEPLOYMENT import *


@step("I start the Scenario to Register Image Valid9m into the EOCM")
def step_impl(context):
    create_dummy_mme_image()
    


@step("I start the Scenario to Create a Flavor EOST-valid9m_flavor")
def step_impl(context):
    create_dummy_mme_flavors()
    




@step("I start the Scenario to Onboard the ECDE_mme_networks_vlan.ovf to cloud manager")
def step_impl(context):
   onboard_dummy_mme_ovf()
   


@step("I start the Scenario to Deploy the ECDE_mme_networks_vlan.ovf")
def step_impl(context):
    deploy_dummy_mme_ovf()
    



@step("I start the Scenario to Onboard the ECDE_HOT-MME-DUMY-VNF.zip as a HOT package to cloud manager")
def step_impl(context):
    onboard_dummy_mme_package()


@step("I start the Scenario to Deploy the ECDE_HOT-MME-DUMY-VNF.zip")
def step_impl(context):
    deploy_dummy_mme_package()


@step("I start the Scenario to Verify the Deployment of dummy mme node")
def step_impl(context):
    verify_dummy_mme_deployment()