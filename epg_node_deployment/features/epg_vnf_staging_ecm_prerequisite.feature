Feature: EPG NODE PRE-REQUISITES ON EO-CM FOR VNF-STAGING


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




