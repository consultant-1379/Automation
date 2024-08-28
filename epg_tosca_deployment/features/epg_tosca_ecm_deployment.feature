Feature: EPG TOSCA NODE DEPLOYMENT FROM EOCM


  Scenario: Upload VNFD in ECM
    Given I start the Scenario to Upload VNFD in ECM

  Scenario: Verify onboarded VNFD package
    Given I start the Scenario to Verify onboarded VNFD package

  Scenario: Create NSD package
    Given I start the Scenario to Create NSD package

  Scenario: Upload NSD package
    Given I start the Scenario to Upload NSD package

  Scenario: Create NS for TOSCA EPG
    Given I start the Scenario to Create NS for TOSCA EPG


  Scenario: Instantiate NS for TOSCA EPG
    Given I start the Scenario to Instantiate NS for TOSCA EPG


  Scenario: Verification of EPG node deployment
    Given I start the Scenario of checking ECM order status for tosca EPG
    Then  I start the Scenario of checking LCM workflow for tosca EPG
    Then  I start the Scenario of pinging the deployed Node
    Then  I start the Scenario of checking sync status of epg tosca in ENM
    
 