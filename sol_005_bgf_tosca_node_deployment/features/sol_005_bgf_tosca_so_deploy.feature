Feature: SOL 005 TOSCA BGF NODE DEPLOYMENT FROM SO



  Scenario: Copy SSH key on LCM
    Given I start the Scenario to copy SSH key on LCM
    

  Scenario: Upload TOSCA SOL BGF VNFD
    Given I start the Scenario to Upload TOSCA SOL BGF VNFD


   Scenario: Verify onboarded TOSCA BGF package
    Given I start the Scenario to Verify onboarded TOSCA BGF package

    
  Scenario: Search TOSCA SOL vBGF image id and transfer it to VIM
    Given I start the Scenario to Search TOSCA SOL vBGF image id and transfer it to VIM
    
    
  Scenario: Create TOSCA SOL BGF NSD
    Given I start the Scenario to Create TOSCA SOL BGF NSD


  Scenario: Upload TOSCA SOL BGF NSD
    Given I start the Scenario to Upload TOSCA SOL BGF NSD


  Scenario: Onboard the ECM SOL005 adapter subsystem to SO
    Given I start the Scenario to onboard ECM SOL005 adapter subsystem to SO


  Scenario: Onboard the configuration templates for SOL BGF
    Given I start the Scenario to onboard the configuration templates for SOL BGF    


  Scenario: Onboard Service template
    Given I start the Scenario to onboard service template


  Scenario: Create Network Service
    Given I start the Scenario to create the network service using serviceModel ID


  Scenario: Polling the state of network service
    Given I start the Scenario of polling the state of network service using service ID
