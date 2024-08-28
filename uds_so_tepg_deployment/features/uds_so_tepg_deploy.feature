Feature: EPG TOSCA NODE DEPLOYMENT FROM SO



  Scenario: Upload VNFD in ECM
    Given I start the Scenario to Upload VNFD in ECM

  Scenario: Verify onboarded VNFD package
   Given I start the Scenario to Verify onboarded VNFD package

  Scenario: Create NSD package
    Given I start the Scenario to Create NSD package

  Scenario: Upload NSD package
    Given I start the Scenario to Upload NSD package

  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO

  Scenario: Create Network Service for EPG deployment using UDS service template
    Given I start the Scenario to Create Network Service for EPG deployment using UDS service template

  Scenario: Polling the state of network service using service ID
    Given I start the Scenario of Polling the state of network service using service ID

  Scenario: Checking LCM workflow
    Given I start the Scenario of Checking LCM workflow

  Scenario: Checking ECM order status
    Given I start the Scenario of Checking ECM order status
