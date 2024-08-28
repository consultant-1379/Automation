Feature: 03- LCM POST INSTALLATION TASKS FOR STATIC PROJECT(WITH vENM)


  Scenario: Change the VNF-LCM service server password at first login
    Given I proceed to change password for VNF-LCM deployed in static project
    


  Scenario: Deploy VNFLCM workflow
    Given I proceed to deploy VNFLCM workflow in static project


  Scenario: VNF-LCM to ECM Integration
    Given I proceed to integrate ECM with VNF-LCM


  Scenario: Change the VNF-LCM DB server password at first login
    Given I proceed to change db server password for static project
