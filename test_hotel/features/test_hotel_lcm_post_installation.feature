Feature: TEST HOTEL LCM POST INSTALLATION TASKS


  Scenario: VNF-LCM to ECM Integration ECM steps
    Given I proceed to run ECM steps for Integration
    

  Scenario: VNF-LCM to ECM Integration LCM steps
    Given I proceed to run LCM steps for Integration


  Scenario: Deploy VNFLCM workflow
    Given I proceed to deploy VNFLCM workflow in static project

    
  Scenario: Change the VNF-LCM DB server password at first login
    Given I proceed to change db server password for static project