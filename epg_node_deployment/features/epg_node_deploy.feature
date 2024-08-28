Feature: EPG NODE DEPLOYMENT FROM EO-CM


  Scenario: Remove old LCM entry from known_hosts file on Host server
    Given I start the Scenario to Remove old LCM entry from known_hosts file on Host server


  Scenario: Add admin and heat_stack_owner roles to project user
    Given I start the Scenario to Add admin and heat_stack_owner roles to project user


  Scenario: Update VNFLCM OSS Password
    Given I start the Scenario to Update VNFLCM OSS Password


  Scenario: Copy the EPG software from HOST blade to VNF-LCM
    Given I start the Scenario to Copy the EPG software from HOST blade to VNF-LCM


  Scenario: Extract EPG software on VNF-LCM Server
    Given I start the Scenario to Extract EPG software on VNF-LCM Server


  Scenario: Install the vEPG workflow on VNF-LCM
    Given I start the Scenario to Install the vEPG workflow on VNF-LCM


  Scenario: Generate ssh keys using JBOSS user
    Given I start the Scenario to Generate ssh keys using JBOSS user


  Scenario: Create Flavors for EPG deployment
    Given I start the Scenario to Create Flavors for EPG deployment


  Scenario: Register Images for EPG deployment
    Given I start the Scenario to Register Images for EPG deployment


  Scenario: Update Onboard file for EPG package onboarding
    Given I start the Scenario to Update Onboard file for EPG package onboarding


  Scenario: Start onboarding the EPG package
    Given I start the Scenario to Start onboarding the EPG package


  Scenario: Verify onboarded EPG package
    Given I start the Scenario to Verify onboarded EPG package


  Scenario: Update deploy file for EPG Node deployment
    Given I start the Scenario to Update deploy file for EPG Node deployment


  Scenario: Start deploying the EPG Node
    Given I start the Scenario to Start deploying the EPG Node


  Scenario: Verify deployed EPG Node
    Given I start the Scenario to Verify deployed EPG Node