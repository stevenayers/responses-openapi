Feature: Pytest Plugin Integration
  As a developer
  I want to use responses-openapi as a pytest plugin
  So that I can mock API responses based on OpenAPI specifications

  Background:
    Given a valid OpenAPI specification file

  Scenario: Plugin registers with pytest
    When the pytest configuration is initialized
    Then the openapi_mock marker should be registered
    And the openapi_mocker fixture should be available

  Scenario: Using the openapi_mock marker
    Given a test function with openapi_mock marker
    When the test is executed
    Then the OpenAPI mocker should be initialized with the spec
    And the responses should be mocked according to the spec

  Scenario: Using the openapi_mocker fixture
    Given a test function using the openapi_mocker fixture
    When the fixture is requested
    Then an OpenAPIMocker instance should be provided
    And the mocker should be cleaned up after the test

  Scenario: Configuring plugin via pytest.ini
    Given a pytest.ini file with openapi configuration
    When pytest loads the configuration
    Then the plugin should use the configured settings
    And the default spec path should be loaded if specified

  Scenario: Configuring plugin via environment variables
    Given environment variables for openapi configuration
    When the plugin initializes
    Then environment settings should override defaults
    But pytest.ini settings should override environment variables

  Scenario: Plugin cleanup after test
    Given a test using openapi_mock marker
    When the test completes
    Then all mocked responses should be cleared
    And no responses should leak to other tests

  Scenario: Multiple specs in single test session
    Given multiple tests with different OpenAPI specs
    When tests are run in sequence
    Then each test should use its own spec
    And specs should not interfere with each other

  Scenario: Plugin error handling for missing spec
    Given a test with openapi_mock marker but no spec
    When the test is executed
    Then a helpful error message should be displayed
    And the test should fail with appropriate error

  Scenario: Plugin with base URL configuration
    Given an openapi_mock marker with base_url option
    When mocked endpoints are registered
    Then all endpoints should use the configured base URL
    And requests to the base URL should be intercepted
