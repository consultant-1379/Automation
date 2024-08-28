
from behave import *
from com_ericsson_do_auto_integration_scripts.UDS_VNF_PRE_REQ import UDS_VNF_PRE_REQ as uds_vnf_pre_req

@step("I start the Scenario to Create VLM and Submit VLM")
def step_impl(context):
    uds_vnf_pre_req.create_vlm(uds_vnf_pre_req)
    
@step("I start the Scenario to Create VSP and Attach Package")
def step_impl(context):    
    uds_vnf_pre_req.create_vsp(uds_vnf_pre_req)


@step("I start the Scenario to Process VSP")
def step_impl(context):    
    uds_vnf_pre_req.process_vsp(uds_vnf_pre_req)
    

@step("I start the Scenario to Commit VSP and Submit VSP")
def step_impl(context):    
    uds_vnf_pre_req.commit_vsp(uds_vnf_pre_req)


@step("I start the Scenario to Create VSP Package Import VSP as VF and Certify VF")
def step_impl(context):    
    uds_vnf_pre_req.create_vsp_package(uds_vnf_pre_req)
    
    
@step("I start the Scenario to Create VNF Service Add VF to VNF Service Certify Service and Distribute Service")
def step_impl(context):    
    uds_vnf_pre_req.create_vnf_service(uds_vnf_pre_req)
    
