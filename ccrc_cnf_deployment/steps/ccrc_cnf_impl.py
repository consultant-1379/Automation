from behave import step
from com_ericsson_do_auto_integration_scripts.CCRC_CNF_DEPLOYMENT import (onboard_ccrc_cnf_package, ccrc_verify_cnf,
                                                                          onboard_ccrc_vnf_package, terminate_ccrc_cnf,
                                                                          ccrc_instantiate_cnf, delete_ccrc_vnf_package,
                                                                          verify_ccrc_cnf_onboarding, ccrc_cleanup,
                                                                          create_ccrc_vnf_identifier, scale_in_ccrc_cnf,
                                                                          verify_ccrc_cnf_terminate, scale_out_ccrc_cnf,
                                                                          delete_ccrc_vnf_identifier,
                                                                          ccrc_secret_creation, terminate_ccrc_cnf_all,
                                                                          upgrade_ccrc_cnf_package, ccrc_verify_upgrade,
                                                                          get_aspect_id_for_scale,
                                                                          verify_ccrc_cnf_scale_out,
                                                                          verify_ccrc_cnf_scale_in)


# ######################################################### ONBOARD JOB ##############################################


@step("I start the Scenario to Create VNF Package Resource ID")
def step_impl(context):
    onboard_ccrc_vnf_package()


@step("I start the Scenario to Create VNFD ID")
def step_impl(context):
    onboard_ccrc_cnf_package()


@step("I start the Scenario to verify the CCRC CSAR Package")
def step_impl(context):
    verify_ccrc_cnf_onboarding()


# ######################################################### DEPLOY JOB ################################################


@step("I start the Scenario to Create VNF Identifier")
def step_impl(context):
    create_ccrc_vnf_identifier()


@step("I start the Scenario to Instantiate the CNF")
def step_impl(context):
    ccrc_instantiate_cnf()


@step("I start the Scenario to Verify CNF Instantiation")
def step_impl(context):
    ccrc_verify_cnf()


# ######################################################### TERMINATE JOB #############################################


@step("I start the Scenario to Terminate the CNF")
def step_impl(context):
    terminate_ccrc_cnf()


@step("I start the Scenario to Verify CNF Termination")
def step_impl(context):
    verify_ccrc_cnf_terminate()


@step("I start the Scenario to Cleanup after CNF Termination")
def step_impl(context):
    ccrc_cleanup()


@step("I start the Scenario to Delete VNF Identifier")
def step_impl(context):
    delete_ccrc_vnf_identifier()


@step("I start the Scenario to Delete CCRC vnf package")
def step_impl(context):
    delete_ccrc_vnf_package()


@step("I start the Scenario to Terminate the packages and resources on EVNFM")
def step_impl(context):
    terminate_ccrc_cnf_all()


# ######################################################### UPGRADE JOB ###############################################


@step("I start the Scenario to Create VNF Package Resource ID upgrade")
def step_impl(context):
    onboard_ccrc_vnf_package()


@step("I start the Scenario to Onboarding the  CCRC CSAR Package to Upgrade")
def step_impl(context):
    onboard_ccrc_cnf_package(upgrade=True)


@step("I start the Scenario to Verifying the Upgrade CCRC CSAR Package")
def step_impl(context):
    verify_ccrc_cnf_onboarding(upgrade=True)


@step("I start the Scenario to Upgrade CCRC")
def step_impl(context):
    upgrade_ccrc_cnf_package()


@step("I start the Scenario to verify  Upgrade CCRC")
def step_impl(context):
    ccrc_verify_upgrade()


# ######################################################### SCALE JOB ################################################


@step("I start the Scenario to Get Aspect id for scale")
def step_impl(context):
    get_aspect_id_for_scale()


@step("I start the Scenario to Scale out CCRC CNF")
def step_impl(context):
    scale_out_ccrc_cnf()


@step("I start the Scenario to Verify Scale out CCRC CNF")
def step_impl(context):
    verify_ccrc_cnf_scale_out()


@step("I start the Scenario to Scale in CCRC CNF")
def step_impl(context):
    scale_in_ccrc_cnf()


@step("I start the Scenario to Verify Scale in CCRC CNF")
def step_impl(context):
    verify_ccrc_cnf_scale_in()


# ##################################################### CCRC Secret Creation##########################################


@step("I start the Scenario to Create CCRC Secret")
def step_impl(context):
    ccrc_secret_creation()
