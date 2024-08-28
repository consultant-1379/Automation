Feature: EPG TOSCA NSD PRE-REQUISITES


  Scenario: Remove old LCM entry from known_hosts file on Host server
    Given I start the Scenario to Remove old LCM entry from known_hosts file on Host server


  Scenario: Add admin and heat_stack_owner roles to project user
    Given I start the Scenario to Add admin and heat_stack_owner roles to project user


  Scenario: Update VNFLCM OSS Password
    Given I start the Scenario to Update VNFLCM OSS Password


  Scenario: Register Images for EPG TOSCA deployment
    Given I start the Scenario to Register Images for EPG TOSCA deployment


  Scenario: Create Flavors for EPG TOSCA deployment
    Given I start the Scenario to Create Flavors for EPG TOSCA deployment


  Scenario: Copy EPG workflow software from HOST blade to VNF-LCM
    Given I start the Scenario to Copy EPG workflow software from HOST blade to VNF-LCM


  Scenario: Install the vEPG workflow on VNF-LCM
    Given I start the Scenario to Install the vEPG workflow on VNF-LCM


  Scenario: Prepare VNFD package
    Given I start the Scenario to Prepare VNFD package