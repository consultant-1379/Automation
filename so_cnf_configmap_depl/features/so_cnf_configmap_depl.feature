Feature: CNF CONFIG-MAP DEPLOYMENT FROM SO


  Scenario: Create NSD Package
    Given I start the Scenario to create NSD package
    
  Scenario: Upload ETSI Tosca NSD packages
    Given I start the Scenario to Upload etsi toscs nsd packages


  Scenario: Upload CNF CONFIG-MAP Config templates on SO 
    Given I start the Scenario to onboard cnf config-map config templates on so


  Scenario: Onboard the CNF CONFIG-MAP subsystem on SO
    Given I start the Scenario to create the subsystem on SO


  Scenario: Upload SOL CNF Service templates
    Given I start the Scenario to upload sol cnf service templates 


  Scenario: Deploy SOl CNF network service
    Given I start the Scenario to deploy the sol cnf netwrok service

  Scenario: Verify SOL CNF network service
    Given I start the Scenario to verify the sol cnf network service
  
  