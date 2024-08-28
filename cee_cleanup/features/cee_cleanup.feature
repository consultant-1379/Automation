
Feature: 01- CEE CLEANUP TASKS

  Scenario: Create openrc files for static and dynamic project
    Given I have user inputs for CEE cleanup
    And I start execution of usecase
    Then I create openrc files for static and dynamic project

  Scenario: Check Project exists in CEE before cleanup
    Given I have user inputs for CEE cleanup
    Then I check for project exists in CEE

  Scenario: Deregister vCisco License
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to deregister vCisco license

  Scenario: Delete stacks from CEE
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to delete stacks from CEE

  Scenario: Delete vm instance from CEE
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to delete vm instance from CEE

  Scenario: Delete cinder volume from CEE
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to delete cinder volume from CEE

  Scenario: Delete internal and external networks with ports from CEE
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to delete networks and ports


  Scenario: Delete flavor from CEE
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to delete flavor from CEE


  Scenario: Delete project from CEE
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to delete project from CEE


  Scenario: Delete users from CEE
    Given I have user inputs for CEE cleanup
    Then I start the Scenario to delete users from CEE
    And I end the execution of tasks


