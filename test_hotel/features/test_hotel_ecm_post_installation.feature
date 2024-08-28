Feature: TEST HOTEL ECM POST INSTALLATION TASKS



  Scenario: Site creation task
    Given I start the Scenario to create the site

  Scenario: Create openrc files for static and dynamic project
    Given I have user inputs for CEE cleanup
    Then I create openrc files for static and dynamic project
	
  Scenario: Create sync proj tenant
    Given I start the Scenario to create sync proj tenant

  Scenario: Vim registration task
    Given I start the Scenario to register the Vim
    
    Scenario: Create Availability Zone
    Given I Start the Scenario to create availability zone
  
  Scenario: Create new sync project
    Given I start the Scenario to create new sync project

  Scenario: Sync Proj ID's
    Given I start the Scenario to fetch sync proj id
    
  Scenario: Register Sync existing project
    Given I start the Scenario to create sync existing project

  Scenario: Create sync project VDC
    Given I start the Scenario to create sync project VDC

   Scenario: Fetch External Network Id
    Given I start the Scenario to fetch the existing provider network id
    
  Scenario: Put runtime file
    Given I start the Scenario to transfer runtime file with updated value
    
