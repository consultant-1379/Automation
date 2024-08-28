Feature: 11- EPG NODE DEPLOYMENT FROM SO


  Scenario: Update Onboard file for EPG package onboarding
    Given I start the Scenario to Update Onboard file for EPG package onboarding


  Scenario: Start onboarding the EPG package
    Given I start the Scenario to Start onboarding the EPG package


  Scenario: Verify onboarded EPG package
    Given I start the Scenario to Verify onboarded EPG package

  Scenario: Transfer So files to workflow pod
    Given I start the Scenario to Transfer So files to workflow pod

  Scenario: Fetch NSD package from ECM to prepare ns1.yaml file
    Given I start the Scenario to Fetch NSD package from ECM to prepare ns1.yaml file


  Scenario: Update NSD package and CSAR it
    Given I start the Scenario to Update NSD package and CSAR it


  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO


  Scenario: Start onboarding the NSD package
    Given I start the Scenario to Start onboarding the NSD package


  Scenario: Onboard Service template for Node deployment
    Given I start the Scenario to onboard service template for node deployment

  Scenario: Create Network Service for Node deployment
    Given I start the Scenario to create the network service using serviceModel ID for Node deployment


  Scenario: Verification of EPG node deployment
    Given I start the Scenario of polling the state of network service using service ID for deployed node
    Then  I start the Scenario of checking LCM workflow
    Then  I start the Scenario of checking bulk configuration
    
    
    
   