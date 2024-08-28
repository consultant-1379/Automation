Feature:  CHECK FOR UNAPPROVED SERVICES AND PODS DEPLOYED

  Scenario: collect resources deployed and check for unapproved resources
    Given I start the Scenario to collect resources deployed

  Scenario: collect details of resources deployed and check_for_unapproved_resources_details
    Given I start the Scenario to collect details of resources
    Then I start the Scenario to check_for_unapproved_resources_details
