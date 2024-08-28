Feature: DUMMY VNF DEPLOYMENT FROM SERVICE ORCHESTRATOR (SO) WITH VNF-LCM VM SHUTDOWN


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


  Scenario: Update NS.yaml file and transfer the NSD package (.CSAR) to ECM
    Given I start the Scenario to update and transfer the NSD package


  Scenario: Onboard the ECM and ENM subsystems to SO
    Given I start the Scenario to Onboard the ECM and ENM subsystems to SO

  Scenario: Deploy NSD package on ECM and Update nsd_id in service template
    Given I start the Scenario to Deploy NSD package on ECM and Update nsd_id in service template


  Scenario: Onboard Service template
    Given I start the Scenario to onboard service template

  Scenario: Create Network Service
    Given I start the Scenario to create the network service using serviceModel ID


  Scenario:  Fetching the service and db hostname
    Given I proceed to fetch the service and db hostname
 

  Scenario:  Shutting Down the Service and DB Hostname
    Given I proceed to shutdown the service and db hostname for "Static"


  Scenario: Polling the state of network service
    Given I start the Scenario of polling the state of network service using service ID
    

   
  Scenario: Change the VNF-LCM service server password at first login
    Given I proceed to change password for VNF-LCM deployed in static project  
        

  Scenario: Change the VNF-LCM DB server password at first login
    Given I proceed to change db server password for static project
    
  