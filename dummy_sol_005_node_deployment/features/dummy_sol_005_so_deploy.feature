Feature: SOL 005 DUMMY NODE DEPLOYMENT FROM SO

    
  Scenario: Create SOL Dummy NSD
    Given I start the Scenario to Create SOL Dummy NSD


  Scenario: Upload SOL Dummy NSD
    Given I start the Scenario to Upload SOL Dummy NSD
	
  Scenario: Onboard the ECM SOL005 adapter subsystem to SO
    Given I start the Scenario to onboard ECM SOL005 adapter subsystem to SO


  Scenario: Onboard the configuration templates for SOL Dummy
    Given I start the Scenario to onboard the configuration templates for SOL Dummy    


  Scenario: Onboard Service template
    Given I start the Scenario to onboard service template


  Scenario: Create Network Service
    Given I start the Scenario to create the network service using serviceModel ID


  Scenario: Polling the state of network service
    Given I start the Scenario of polling the state of network service using service ID

    
    