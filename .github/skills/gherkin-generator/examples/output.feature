Feature: Payment card management
  In order to complete payment processing
  As a registered shopper
  I want to save my payment card information securely.

  @positive @TC-001
  Scenario: Save payment card successfully
    Given the user is logged in
    And the user provides valid payment card details
    When the user submits the payment card information
    Then the payment card is stored securely
