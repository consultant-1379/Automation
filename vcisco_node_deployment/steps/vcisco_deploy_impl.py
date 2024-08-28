
from behave import *
from com_ericsson_do_auto_integration_scripts.VCISCO_DEPLOY import *




@step("I start the Scenario to create security group")
def step_impl(context):    
    create_security_groups()
    

@step("I start the Scenario to create vCisco flavours")
def step_impl(context):    
    create_vCisco_flavours()


@step("I start the Scenario to create valid9m flavours")
def step_impl(context):    
    create_valid9m_flavours()
    

@step("I start the Scenario to create vCisco Image")
def step_impl(context):    
    register_vCisco_images()    
    


@step("I start the Scenario to onboard OVF")
def step_impl(context):    
    onboard_ovf()
    

@step("I start the Scenario to deploy OVF")
def step_impl(context):    
    deploy_ovf()
    

    
@step("I start the Scenario to deploy Network")
def step_impl(context):    
    deploy_asr_network()
    
	
@step("I start the Scenario to create bgw port")
def step_impl(context):    
    create_vcisco_bgw_ports()
    


@step("I start the Scenario to deploy vCisco")
def step_impl(context):    
    deploy_vcisco()
    


@step("I start the Scenario to verify vCisco deploy")
def step_impl(context):    
    verify_vcisco_deployment()
    
    
@step("I start the Scenario to disable port")
def step_impl(context):    
    disable_port()
    

@step("I start the Scenario to register vCisco license")
def step_impl(context):    
    register_vcisco_license()