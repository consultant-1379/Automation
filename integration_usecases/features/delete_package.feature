# Created by eshetra at 10/9/2018

Feature: 06- TERMINATE AND DELETE DUMMY VNF FROM ECM


  Scenario: Update terminate.json
    Given I have user inputs
    Then I update the json file "terminate.json"


  Scenario Outline: Put terminate.json on ECM host blade server
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And I fetch the file from local directory
    Then I put "<file>" on server
    And close the connection
    Examples:
            |file|
            |terminate.json|


  Scenario: Terminating the vAPP
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And I fetch the Auth token
    And I fetch the core_vm_ip
    And I fetch the vApp id
    Then I create the curl command for delete vApp
    Then I execute the curl command
    Then I verify the curl command response for deletion
    Then close the connection



  Scenario: Verification of vAPP termination
    Given I have an IP address
    And I have userID and password
    Then I login to server
    Given I have a connection with server
    And I fetch the external_ip_for_services_vm
    Then I create the command of pinging the external_ip_for_services_vm
    Then I execute the ping command
    Then I verify the vApp Deletion
    Then close the connection

