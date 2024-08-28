Feature: DUMMY VNF DEPLOYMENT FROM SERVICE ORCHESTRATOR (SO) WITH VM VNFM


  Scenario: Update VNFD_Wrapper_VNFLAF.json
    Given I have user inputs
    Then I update the json file "VNFD_Wrapper_VNFLAF.json"

  Scenario: Update vnflaf_cee-env.yaml file
    Given I have user inputs
    Then I update the json file "vnflaf_cee-env.yaml"


  Scenario: Create the vnflaf dir on server
    
    Given fetch local dir path
    And I fetch the file from local directory
    Then I move dir to path "/vnflcm-ext/current/vnf_package_repo/"
    

  Scenario: Update NS.yaml file and transfer the NSD package (.CSAR) to ECM
    Given I start the Scenario to update and transfer the NSD package


  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO

  Scenario: Deploy NSD package on ECM and Update nsd_id in service template
    Given I start the Scenario to Deploy NSD package on ECM and Update nsd_id in service template


  Scenario: Onboard Service template
    Given I start the Scenario to onboard service template

  Scenario: Create Network Service
    Given I start the Scenario to create the network service using serviceModel ID


  Scenario: Polling the state of network service
    Given I start the Scenario of polling the state of network service using service ID
    
  Scenario: Verify Dummy Node Deploy Workflow Version
    Given I start the Scenario to verify dummy node deploy workflow version
    
   
    
    
