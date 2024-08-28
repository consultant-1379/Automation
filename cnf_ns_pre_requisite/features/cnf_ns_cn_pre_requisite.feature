Feature:  CNF-NS INSTANTIATION PRE-REQUISITES ON CLOUD NATIVE EO-CM

  Scenario: Retrieve HELM repo details from EVNFM
    Given I start the Scenario to retrieve HELM repo details from EVNFM

  Scenario: Retrieve and update HELM certificate
    Given I start the Scenario to fetch helm certificate

  Scenario: Retrieve Docker registry details from EVNFM
    Given I start the Scenario to retrieve Docker registry details from EVNFM

  Scenario: Retrieve a docker registry certificate
    Given I start the Scenario to fetch docker registry certificate

  Scenario: Add NFVO configuration on EVNFM
    Given I start the Scenario to execute post install script to add NFVO configuration on EVNFM

  Scenario: Register EVNFM staging for CNF Integration
    Given I start the Scenario to register EVNFM for CNF integration

  Scenario: Restart pods in cloud native EOCM
    Given I start the scenario to restart the eocm cn pods
