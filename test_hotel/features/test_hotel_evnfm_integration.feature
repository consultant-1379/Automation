Feature:  EVNFM INTEGRATION FOR TEST HOTEL

  Scenario: Take back up of a baseenv file
    Given I start the Scenario to take a back up of a baseenv file


  Scenario: Retrieve HELM repo details from EVNFM
    Given I start the Scenario to retrieve HELM repo details from EVNFM


  Scenario: Retrieve Docker registry details from EVNFM
    Given I start the Scenario to retrieve Docker registry details from EVNFM


  Scenario: Retrieve a docker registry certificate
    Given I start the Scenario to fetch docker registry certificate

   Scenario: update the baseenv file
    Given I start the Scenario to update the baseenv file with the new values


  Scenario: configure HELM and Docker registry service
    Given I start the Scenario to configure Docker and HELM registry service


  Scenario: After EO-CM configured verify the updated values in baseenv file
    Given I start the Scenario to verify the updated values in baseenv file



  Scenario: Add NFVO configuration on EVNFM
    Given I start the Scenario to execute post install script to add NFVO configuration on EVNFM


  Scenario: Register EVNFM staging for CNF Integration
    Given I start the Scenario to register EVNFM for CNF integration

