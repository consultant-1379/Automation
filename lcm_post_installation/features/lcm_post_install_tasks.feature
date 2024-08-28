Feature: 3- LCM POST INSTALLATION TASKS


  Scenario: Change the VNF-LCM service server password at first login
    Given I have user inputs
    Then I proceed to change password


  Scenario: Deploy VNFLCM workflow
    Given I have user inputs
    Then I proceed to deploy VNFLCM workflow


  Scenario: VNF-LCM to ECM Integration
    Given I proceed to integrate ECM with VNF-LCM


  Scenario: Change the VNF-LCM DB server password at first login
    Given I proceed to change db server password
