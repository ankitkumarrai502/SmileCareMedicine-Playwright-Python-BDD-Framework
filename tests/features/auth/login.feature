@auth
Feature: Customer Login
  As a registered SmileCare customer
  I want to log in with my email and password
  So that I can access my account

  Background:
    Given the login page is open

  @smoke
  Scenario: AUTH-001 Login page renders all key elements
    Then the login form shows the email, password fields and the Log In button
    And the signup and forgot-password links are visible

  @smoke @needs_auth
  Scenario: AUTH-002 Successful login with valid credentials
    When I log in with valid credentials
    Then I land on the home page
    And I am logged in

  @needs_auth
  Scenario: AUTH-003 Session persists after a page reload
    When I log in with valid credentials
    And I reload the page
    Then I am logged in

  Scenario: AUTH-004 Sign-up link navigates to the signup page
    When I click the sign-up link
    Then the URL path is "/signup"

  Scenario: AUTH-005 Password show/hide toggle reveals and re-masks the password
    When I type a password into the password field
    And I toggle password visibility
    Then the password is shown as plain text
    When I toggle password visibility
    Then the password is masked

  Scenario: AUTH-006 Email field uses an email input type
    Then the email field has type "email"

  @smoke
  Scenario: AUTH-007 Wrong password is rejected
    When I log in with the valid email and a wrong password
    Then I see the invalid-credentials error
    And I am not logged in

  Scenario: AUTH-008 Unregistered email is rejected
    When I submit the login form with email "nouser-xyz@example.com" and password "Whatever1!"
    Then I see the invalid-credentials error
    And I am not logged in

  Scenario Outline: <id> Client validation blocks an incomplete or malformed submit
    When I submit the login form with email "<email>" and password "<password>"
    Then I remain on the login page
    And I am not logged in

    Examples:
      | id       | email       | password       |
      | AUTH-009 |             |                |
      | AUTH-010 | VALID_EMAIL |                |
      | AUTH-011 |             | VALID_PASSWORD |
      | AUTH-012 | foo@        | VALID_PASSWORD |

  Scenario: AUTH-014 Valid email wrapped in whitespace is handled gracefully
    When I log in with the valid email wrapped in whitespace
    Then the app responds without a crash

  Scenario: AUTH-015 Email is case-insensitive
    When I log in with the valid email in uppercase
    Then I am logged in

  Scenario: AUTH-016 Password is case-sensitive
    When I log in with the valid email and a wrong-case password
    Then I see the invalid-credentials error
    And I am not logged in

  Scenario: AUTH-017 Very long inputs are handled gracefully
    When I submit very long credentials
    Then I am not logged in
    And the app responds without a crash

  Scenario Outline: <id> Injection payloads are safely rejected
    When I submit the login form with email "<email>" and password "<password>"
    Then I am not logged in
    And no browser dialog appears

    Examples:
      | id       | email          | password                  |
      | AUTH-018 | ' OR 1=1 --    | <script>alert(1)</script> |

  Scenario: AUTH-019 Forgot Password link leads to a reset flow
    When I click the forgot-password link
    Then I am taken away from the login form to a password reset flow

  @needs_auth
  Scenario: AUTH-020 Rapid double submit logs in exactly once without error
    When I log in with valid credentials clicking submit twice
    Then I am logged in
