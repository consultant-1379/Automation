Feature: EPG TOSCA NODE DEPLOYMENT FROM SO


  
  Scenario: Upload VNFD in ECM
    Given I start the Scenario to Upload VNFD in ECM
    
  Scenario: Verify onboarded VNFD package
   Given I start the Scenario to Verify onboarded VNFD package

  Scenario: Create NSD package 
    Given I start the Scenario to Create NSD package
    
  Scenario: Upload NSD package 
    Given I start the Scenario to Upload NSD package
    
  Scenario: Transfer So files to workflow pod
   Given I start the Scenario to Transfer So files to workflow pod
   
  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO
    
  Scenario: Upload additional parameter config files into the SO 
    Given I start the Scenario to Upload additional parameter config files into the SO
    
  Scenario: Onboard service template for node deployment
    Given I start the Scenario to Onboard service template for node deployment
  
  Scenario: Create the network service using serviceModel ID for Node deployment
    Given I start the Scenario to Create the network service using serviceModel ID for Node deployment
  
  Scenario: Verification of EPG node deployment
    Given I start the Scenario of polling the state of network service using service ID for deployed node
    Then  I start the Scenario of pinging the deployed Node
    Then  I start the Scenario of checking sync status of node in ENM
    
 