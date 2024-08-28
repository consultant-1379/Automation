Feature: EPG NODE PRE-REQUISITES VM-VNFM AND EO-CM


  Scenario: Add admin and heat_stack_owner roles to project user
    Given I start the Scenario to Add admin and heat_stack_owner roles to project user


  Scenario: Transfer the EPG software from HOST blade to VM-VNFM
    Given I start the Scenario to Copy the EPG software from HOST blade to VNF-LCM


  Scenario: Install the vEPG workflow on VM-VNFM
    Given I start the Scenario to Install the vEPG workflow on VM-VNFM


  Scenario: Generate ssh keys using JBOSS user
    Given I start the Scenario to Generate ssh keys using JBOSS user


  Scenario: Create Flavors for EPG deployment
    Given I start the Scenario to Create Flavors for EPG deployment


  Scenario: Register Images for EPG deployment
    Given I start the Scenario to Register Images for EPG deployment



