Feature: 08- DUMMY VNF DEPLOYMENT FROM SERVICE ORCHESTRATOR (SO)


  Scenario: Update NS.yaml file and transfer the NSD package (.CSAR) to ECM
    Given I start the Scenario to update and transfer the NSD package

  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO
    
  Scenario: Deploy NSD package on ECM and Update nsd_id in service template
    Given I start the Scenario to Deploy NSD package on ECM and Update nsd_id in service template


  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO


  Scenario: Onboard Service template
    Given I start the Scenario to onboard service template

  Scenario: Create Network Service
    Given I start the Scenario to create the network service using serviceModel ID


  Scenario: Polling the state of network service
    Given I start the Scenario of polling the state of network service using service ID
