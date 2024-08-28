# Created by eiaavij at 11/20/2018

Feature: ENM to VNF Integration


  Scenario: Check sudo command
    When Login to Server "LCM Service Server"
    Given I have a command "sudo -i"
    And I execute the sudo commannd
    Then User changes to root User
    And close the connection

  Scenario: Copy key pair file to local
    When Login to Server "LCM Service Server"
    Given Go to path /var/tmp/
    Then I copy the key file to local "key_pair_DO_Maintrack_C4A10.pem"
    And close the connection


  Scenario: Fetching the httpd_internal_ip_list
    When Login to Server "LCM Service Server"
    Given Go to path /home/cloud-user
    Then I fetch the httpd_internal_ip_list from sed.json
    And I save the httpd instances
    And close the connection


  Scenario: Update the /etc/hosts file for first httpd
    When Login to Server "LCM Service Server"
    Then Go to path /var/tmp/
    Given I have httpd instances
    And Login to httpd instance using "key_pair_DO_Maintrack_C4A10.pem"
    Then Update the /etc/hosts/ file with vnflcm ip
    And close the connection

    Scenario: Update the /etc/hosts file for second httpd
    When Login to Server "LCM Service Server"
    Then Go to path /var/tmp/
    Given I have httpd instances
    And Login to httpd instance using "key_pair_DO_Maintrack_C4A10.pem"
    Then Update the /etc/hosts/ file with vnflcm ip
    And close the connection

    #TODO Scenario: Verification of above to be discussed




