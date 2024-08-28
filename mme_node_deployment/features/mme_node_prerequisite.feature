Feature: 14- MME NODE PRE-REQUISITES ON EO-CM


  Scenario: Remove old LCM entry from known_hosts file on Host server
    Given I start the Scenario to Remove old LCM entry from known_hosts file on Host server


  Scenario: Add admin and heat_stack_owner roles to project user
    Given I start the Scenario to Add admin and heat_stack_owner roles to project user


  Scenario: Update VNFLCM OSS Password
    Given I start the Scenario to Update VNFLCM OSS Password


  Scenario: Copy the MME software from HOST blade to VNF-LCM
    Given I start the Scenario to Copy the MME software from HOST blade to VNF-LCM


  Scenario: Install the vMME workflow on VNF-LCM
    Given I start the Scenario to Install the vMME workflow on VNF-LCM


  Scenario: Update db table with MME entries for instantiate and terminate
    Given I start the Scenario to Update db table with MME entries for instantiate and terminate
    

  Scenario: Generate ssh keys using JBOSS user
    Given I start the Scenario to Generate ssh keys using JBOSS user


  Scenario: Create Flavors for MME deployment
    Given I start the Scenario to Create Flavors for MME deployment


  Scenario: Register Images for MME deployment
    Given I start the Scenario to Register Images for MME deployment
  
  Scenario: IPAM for MME deployment
    Given I start the Scenario to upload IPAM for MME deployment



