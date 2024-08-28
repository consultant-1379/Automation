Feature: 16- DUMMY MME DEPLOYMENT USING GVNFM



  Scenario: Register Image into the EOCM
    Given I start the Scenario to Register Image Valid9m into the EOCM

  Scenario: Create a Flavor
    Given I start the Scenario to Create a Flavor EOST-valid9m_flavor


  Scenario: Onboard the ECDE_mme_networks_vlan.ovf to cloud manager
    Given I start the Scenario to Onboard the ECDE_mme_networks_vlan.ovf to cloud manager


  Scenario: Deploy the ECDE_mme_networks_vlan.ovf
    Given I start the Scenario to Deploy the ECDE_mme_networks_vlan.ovf


  Scenario: Onboard the ECDE_HOT-MME-DUMY-VNF.zip as a HOT package to cloud manager
    Given I start the Scenario to Onboard the ECDE_HOT-MME-DUMY-VNF.zip as a HOT package to cloud manager


  Scenario: Deploy the ECDE_HOT-MME-DUMY-VNF.zip
    Given I start the Scenario to Deploy the ECDE_HOT-MME-DUMY-VNF.zip


  Scenario: Verify the Deployment of dummy mme node
    Given I start the Scenario to Verify the Deployment of dummy mme node