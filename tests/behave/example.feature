Feature: Say Hello Function
  As a developer
  I want to test the say_hello function
  So that I can ensure it properly greets users

  Scenario: Greeting with a name
    Given I have a name "Alice"
    When I call say_hello with the name
    Then I should get the greeting "Hello, Alice!"

  Scenario: Greeting with another name
    Given I have a name "Bob"
    When I call say_hello with the name
    Then I should get the greeting "Hello, Bob!"

  Scenario: Greeting with None
    Given I have no name
    When I call say_hello with None
    Then I should get the greeting "Hello, None!"

  Scenario Outline: Greeting multiple people
    Given I have a name "<name>"
    When I call say_hello with the name
    Then I should get the greeting "<greeting>"

    Examples:
      | name    | greeting        |
      | Charlie | Hello, Charlie! |
      | Diana   | Hello, Diana!   |
      | Eve     | Hello, Eve!     |
