Feature: 03- LCM POST INSTALLATION TASKS FOR DYNAMIC PROJECT(WITHOUT vENM)


  Scenario: Change the VNF-LCM service server password at first login
    Given I proceed to change password for VNF-LCM deployed in dynamic project
    


  Scenario: Deploy VNFLCM workflow
    Given I proceed to deploy VNFLCM workflow in dynamic project


  Scenario: Add the NFVO TLS certificate to the VNF-LCM Services VM
    Given I proceed to Add the NFVO TLS certificate to the VNF-LCM Services VM

  
  Scenario: Change the VNF-LCM service server password of Standby Server
    Given I proceed to change password for VNF-LCM Standby Server deployed in dynamic project  
     

  Scenario: Setup the VNFLCM Services Apache Server for Authentication
    Given I proceed to Setup the VNFLCM Services Apache Server for Authentication


  Scenario: Create the VNF-LCM GUI User and password
    Given I proceed to create gui user and password
    

  Scenario: VNF-LCM to ECM Integration without ENM
    Given I proceed to integrate ECM with VNF-LCM without ENM

  
  Scenario: Change the VNF-LCM DB server password at first login
    Given I proceed to change db server password for dynamic project