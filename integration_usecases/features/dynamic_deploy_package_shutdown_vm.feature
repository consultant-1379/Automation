# Created by eiaavij at 10/17/2018 new

Feature: 18- INSTANTIATE AND DEPLOY THE DUMMY VNF PACKAGE EOCM WITH VNF-LCM VM SHUTDOWN (NOT vENM)
  

  Scenario: Update VNFD_Wrapper_VNFLAF.json
    Given I have user inputs
    Then I update the json file "VNFD_Wrapper_VNFLAF.json"

  Scenario: Update vnflaf_cee-env.yaml file
    Given I have user inputs
    Then I update the json file "vnflaf_cee-env.yaml"


  Scenario: Create the vnflaf dir on server
    When Login to Server "VNF-LCM"
    Given fetch local dir path
    And I fetch the file from local directory
    Then I move dir to path "/vnflcm-ext/current/vnf_package_repo/"
    And close the connection


  Scenario: Update deploy.json file
    When Login to Server "ECM Host Blade server"
    Given I have user inputs
    And I fetch the file from local directory
    Then I update the json file "deploy.json"
    And close the connection


  Scenario Outline: Put deploy.json on ECM host blade server
    When Login to Server "ECM Host Blade server"
    Given I have a connection with server
    And I fetch the file from local directory
    Then I put "<file>" on server
    And close the connection
    Examples:
            |file|
            |deploy.json|


  Scenario:  Deploying the package
    When Login to Server "ECM Host Blade server"
    And I fetch the Auth token
    And I fetch the core_vm_ip
    And I fetch the vnf package id
    Then I create the curl command for deploying the package
    And I execute the curl command
    And I save the correlation id    
    And close the connection
    
    

  Scenario:  Fetching the service and db hostname
    Given I proceed to fetch the service and db hostname
    

  Scenario:  Shutting Down the Service and DB Hostname
    Given I proceed to shutdown the service and db hostname for "Dynamic"   
    

  Scenario: Checking the order status of deployed package
    When Login to Server "ECM Host Blade server"
    And I fetch the Auth token
    And I fetch the core_vm_ip
    And I fetch the vnf package id
    And I fetch the correlation Id
    And I check the order status of deployed dummy node   
    And close the connection
   
    

  Scenario: Get the deployed Vapp Id
    When Login to Server "ECM Host Blade server"
    And I fetch the Auth token
    And I fetch the core_vm_ip
    And I fetch the correlation Id
    Then I create the curl command for fetching the vApp id using correlation id
    And I execute the curl command
    And I save the vApp id
    And close the connection


  Scenario:  Wait 120 seconds for verification of Vapp
    When I wait for completion of task for "120" seconds

  Scenario: Wait more 60 seconds
    When I wait 60 seconds for Vapp to come up

  Scenario:  Verification of Deploying Use case
    When Login to Server "ECM Host Blade server"
    And I fetch the Auth token
    And I fetch the core_vm_ip
    And I fetch the vApp id
    And I fetch the external_ip_for_services_vm
    Then I create the curl command of verification of deployed package
    And I execute the curl command
    Then I create the command of pinging the external_ip_for_services_vm
    And I execute the ping command
    Then I verify the deploy usecase
    And close the connection
   

  Scenario: Change the VNF-LCM DB server password at first login
    Given I proceed to change db server password for dynamic project
    


