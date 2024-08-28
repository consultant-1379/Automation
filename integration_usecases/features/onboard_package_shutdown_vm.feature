# Created by emaidns at 10/9/2018

Feature: 04- ONBOARDING THE DUMMY VNF PACKAGE ON ECM WITH VNF-LCM VM SHUTDOWN


  Scenario: Update onboard.json file with user inputs
    Given I have user inputs
    And I fetch the file from local directory
    Then I update the json file "onboard.json"

  Scenario: Update flavour in vnflaf_cee.yaml file for ECM and VNF
    Given I fetch the file from local directory
    Then I update the flavour in files


  Scenario Outline: Put vnflaf_cee.yaml and onboard.json on ECM host blade server
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And I fetch the file from local directory
    Then I put "<file>" on server
    And close the connection

    Examples:
            |file|
            |vnflaf_cee.yaml|
            |onboard.json|


  Scenario: Generate Auth Token on ECM host blade server
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And I fetch the core_vm_ip
    And I create the curl command for auth token
    Then I execute the curl command
    And save the Auth token
    And close the connection


  Scenario: Generate package ID on ECM host blade server
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And I fetch the core_vm_ip
    And I fetch the Auth token
    Then I create the curl command for generating the package id
    And I execute the curl command
    And I save the vnfPackage id
    And close the connection



  Scenario:  Uploading the package on ECM host blade server
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And fetch the values for content range, filechecksum and chunk size
    And I fetch the Auth token
    And I fetch the core_vm_ip
    And I fetch the vnf package id
    Then I create the curl command for uploading the package
    And I execute the curl command
    And I Verify the curl command
    And close the connection


  Scenario:  Verification of Onbording Use case
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And I fetch the Auth token
    And I fetch the core_vm_ip
    And I fetch the vnf package id
    Then I create the curl command for verifying uploading the package
    And I execute the curl command
    Then I verify the onboard usecase
    And close the connection
