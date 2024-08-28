Feature: EPG NODE DEPLOYMENT FROM SO USING ETSI TOSCA NSD PACKAGE FROM ECM

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

  Scenario: Create NS
    Given I start the Scenario to create NS

  Scenario: Instantiate NS
    Given I start the Scenario to instantiate NS

  Scenario: Verification of EPG node deployment
    Given I start the Scenario of checking ECM order status for etsi tosca EPG
    Then  I start the Scenario of checking LCM workflow for etsi tosca EPG
    Then  I start the Scenario of pinging the deployed Node
    Then  I start the Scenario of checking sync status of epg etsi tosca in ENM