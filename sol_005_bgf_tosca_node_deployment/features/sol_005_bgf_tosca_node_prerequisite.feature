Feature: SOL 005 TOSCA BGF NODE PRE-REQUISITES ON EO-CM


  Scenario: Onboard vBGF TOSCA Hot Package
    Given I start the Scenario to Onboard vBGF TOSCA Hot Package


  Scenario: Deploy vBGF TOSCA Hot Package
    Given I start the Scenario to Deploy vBGF TOSCA Hot Package
 
 
  Scenario: Create TOSCA vBGF flavor and transfer to VIM
    Given I start the Scenario to Create TOSCA vBGF flavor and transfer to VIM
    
 
  Scenario: Remove old LCM entry from known_hosts file on Host server
    Given I start the Scenario to Remove old LCM entry from known_hosts file on Host server
    
     
  Scenario: Install the workflow on VNF-LCM
    Given I start the Scenario to Install the workflow on VNF-LCM       

  
  Scenario: Generate ssh keys using JBOSS user
    Given I start the Scenario to Generate ssh keys using JBOSS user


  Scenario: Add package download parameter in VNFLCM
    Given I start the Scenario to Add package download parameter in VNFLCM
