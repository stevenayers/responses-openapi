Feature: Core Mocker Integration
  As a developer
  I want to use the OpenAPIMocker to mock API responses
  So that I can test my application without real API calls

  Scenario: Initialize mocker with specification
    Given an OpenAPI specification file path
    When I create an OpenAPIMocker instance
    Then the spec should be loaded automatically
    And all components should be initialized

  Scenario: Initialize mocker without specification
    When I create an OpenAPIMocker without a spec
    Then the mocker should be created successfully
    And I should be able to load a spec later

  Scenario: Load specification after initialization
    Given an OpenAPIMocker instance without spec
    When I load a specification
    Then all components should be initialized
    And routes should be registered

  Scenario: Register all routes from specification
    Given a mocker with loaded specification
    When routes are registered
    Then all paths from the spec should be registered
    And all HTTP methods should be covered

  Scenario: Mock GET request
    Given a mocker with registered routes
    When a GET request is made to a mocked endpoint
    Then a mock response should be returned
    And the response should match the specification

  Scenario: Mock POST request with body
    Given a mocker with registered routes
    When a POST request is made with a JSON body
    Then the request should be intercepted
    And an appropriate response should be generated

  Scenario: Override specific endpoint response
    Given a mocker with registered routes
    When I override a specific endpoint's response
    And a request is made to that endpoint
    Then the overridden response should be returned
    And not the generated response

  Scenario: Set specific status code for endpoint
    Given a mocker with registered routes
    When I set status code 404 for an endpoint
    And a request is made to that endpoint
    Then a 404 response should be returned
    And the response should use the 404 schema

  Scenario: Context manager usage
    When I use the mocker as a context manager
    Then mocking should start on enter
    And mocking should stop on exit
    And all mocks should be cleaned up

  Scenario: Request validation enabled
    Given a mocker with request validation enabled
    When an invalid request is made
    Then a 400 response should be returned
    And validation errors should be included

  Scenario: Request validation disabled
    Given a mocker with request validation disabled
    When an invalid request is made
    Then the request should be processed anyway
    And a mock response should be generated

  Scenario: Response validation enabled
    Given a mocker with response validation enabled
    When generating a response
    Then the response should be validated
    And invalid responses should raise an error

  Scenario: Response validation disabled
    Given a mocker with response validation disabled
    When generating any response
    Then no response validation should occur
    And responses should be returned as-is

  Scenario: Base URL configuration
    Given a mocker configured with base URL "https://api.example.com"
    When routes are registered
    Then all routes should include the base URL
    And requests to the base URL should be intercepted

  Scenario: Multiple mockers in same test
    Given two different OpenAPIMocker instances
    When both are active simultaneously
    Then they should not interfere with each other
    And each should handle its own endpoints

  Scenario: Cleanup after test
    Given a mocker that has been used
    When cleanup is called
    Then all registered mocks should be removed
    And the responses library should be reset

  Scenario: Handle requests with path parameters
    Given a mocker with parameterized paths
    When a request matches a parameterized path
    Then path parameters should be extracted
    And the correct operation should be called

  Scenario: Handle unmatched requests
    Given a mocker with registered routes
    When a request is made to an unregistered path
    Then the request should not be intercepted
    And it should pass through to the actual handler

  Scenario: Generate responses with examples
    Given a spec with example responses
    When use_examples option is enabled
    Then examples should be preferred over generated data
    And example responses should be returned

  Scenario: Generate responses without examples
    Given a spec without examples
    When a response is generated
    Then data should be generated from schemas
    And hypothesis-jsonschema should be used

  Scenario: Handle circular references
    Given a spec with circular references
    When responses are generated
    Then circular references should be handled
    And generation should not cause infinite loops

  Scenario: Configure Faker locale
    Given a mocker with faker_locale set to "fr_FR"
    When responses with fake data are generated
    Then French locale should be used
    And generated data should be localized

  Scenario: Debug mode logging
    Given a mocker with debug mode enabled
    When requests and responses occur
    Then detailed logs should be generated
    And request/response details should be logged

  Scenario: Integration with responses library
    Given the OpenAPIMocker
    When it operates
    Then it should use responses.RequestsMock internally
    And all responses features should be available
