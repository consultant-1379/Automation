Feature: EPG NODE DEPLOYMENT FROM SO USING ETSI TOSCA NSD PACKAGE


  Scenario: Update Onboard file for EPG package onboarding
    Given I start the Scenario to Update Onboard file for EPG package onboarding


  Scenario: Start onboarding the EPG package
    Given I start the Scenario to Start onboarding the EPG package


  Scenario: Verify onboarded EPG package
    Given I start the Scenario to Verify onboarded EPG package


  Scenario: Create ETSI TOSCA NSD Package
    Given I start the Scenario to Create ETSI TOSCA NSD Package


  Scenario: Upload ETSI TOSCA NSD Package
    Given I start the Scenario to Upload ETSI TOSCA NSD Package


  Scenario: Transfer So files to workflow pod
    Given I start the Scenario to Transfer So files to workflow pod


  Scenario: Onboard the configuration templates for ETSI TOSCA NSD Package
    Given I start the Scenario to onboard the configuration templates for ETSI TOSCA NSD Package


  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO


  Scenario: Onboard service template for node deployment
    Given I start the Scenario to onboard service template for node deployment


  Scenario: Create Network Service for Node deployment
    Given I start the Scenario to create the network service using serviceModel ID for Node deployment


  Scenario: Verification of EPG node deployment
    Given I start the Scenario of polling the state of network service using service ID for deployed node
    Then  I start the Scenario of pinging the deployed Node
    Then  I start the Scenario of checking sync status of node in ENM


#  Scenario: Verify Network Service status
#    Given I start the Scenario to verify the network service status