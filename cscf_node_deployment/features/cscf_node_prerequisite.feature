Feature: CSCF NODE PRE-REQUISITES ON EO-CM



  Scenario: Get VNFD ID from ECM host blade server
    Given I start the Scenario to Get VNFD ID from ECM host blade server


  Scenario: Transfer the CSCF software from HOST blade to VNF-LCM
    Given I start the Scenario to Copy the CSCF software from HOST blade to VNF-LCM


  Scenario: Generate ssh keys using JBOSS user
    Given I start the Scenario to Generate ssh keys using JBOSS user

    
  Scenario: Onboard Network stack for CSCF Node
    Given I start the Scenario to Onboard Network Stack for CSCF node
    
  
  Scenario: Deploy Network stack for CSCF Node
    Given I start the Scenario to Deploy Network Stack for CSCF node