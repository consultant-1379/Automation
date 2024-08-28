Feature: DUMMY TOSCA NODE DEPLOYMENT FROM EO-CM



  Scenario: Remove old vnflaf package from vnflcm
    Given I start the Scenario to Remove old vnflaf package from vnflcm

  Scenario: Create flavor for ETSI TOSCA Dummy Deployment 
    Given I start the Scenario to Create Flavors for ETSI Dummy Tosca deployment
    
  Scenario: Add Package download parameter to VNF-LCM Configuration 
    Given I start the Scenario to add ETSI Dummy Tosca Package download parameter
    
  Scenario: Get VnfId to get package name
    Given I start the Scenario to Get zip package name from ECM host blade server for dummy Tosca
  
  Scenario: Update Onboard file for ETSI Dummy Tosca deployment package onboarding
    Given I start the Scenario to Update Onboard file for ETSI Dummy Tosca Deployment package onboarding

  Scenario: Start onboarding the ETSI Dummy Tosca deployment package
    Given I start the Scenario to Start onboarding the Dummy Tosca deployment package

  Scenario: Verify onboarded ETSI Dummy Tosca package
    Given I start the Scenario to Verify onboarded ETSI Dummy Tosca package

  Scenario: Transfer ETSI dummy Tosca image to openstack
    Given I start the Scenario to transfer ETSI Dummy Tosca image to openstack
    
  Scenario: Update deploy Dummy Tosca ETSI file
    Given I start the Scenario to Update deploy Dummy Tosca ETSI file


  Scenario: Start deploying the ETSI Dummy Tosca Node
    Given I start the Scenario to Start deploying the ETSI Dummy Tosca Node


  Scenario: Verify deployed ETSI Dummy Tosca deployment Node
    Given I start the Scenario to Verify ETSI Dummy Tosca deployment Node 
   
  Scenario: Verify deployed ETSI Dummy Tosca Workflow version
    Given I start the Scenario to Verify ETSI Dummy Tosca Workflow verison
    
    
    
  