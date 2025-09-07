Feature: Schema Validation
  As a developer
  I want to validate requests and responses against OpenAPI schemas
  So that I can ensure API compliance

  Background:
    Given a loaded OpenAPI specification
    And a schema validator initialized with the spec

  Scenario: Validate valid request
    Given a valid GET request to "/pets"
    When I validate the request
    Then no validation errors should be returned
    And the request should be marked as valid

  Scenario: Validate request with invalid path parameter
    Given a GET request to "/pets/invalid-id"
    And the spec requires integer path parameter
    When I validate the request
    Then validation errors should be returned
    And the error should indicate invalid path parameter type

  Scenario: Validate request with missing required query parameter
    Given a GET request missing required query parameter
    When I validate the request
    Then validation errors should be returned
    And the error should indicate missing required parameter

  Scenario: Validate request with invalid query parameter type
    Given a GET request with string instead of integer for "limit"
    When I validate the request
    Then validation errors should be returned
    And the error should indicate type mismatch

  Scenario: Validate POST request with valid body
    Given a POST request with valid JSON body
    When I validate the request
    Then no validation errors should be returned
    And the request body should be marked as valid

  Scenario: Validate POST request with invalid body schema
    Given a POST request with body missing required fields
    When I validate the request
    Then validation errors should be returned
    And the error should list missing required fields

  Scenario: Validate request with invalid content type
    Given a POST request with "text/plain" content type
    And the spec only allows "application/json"
    When I validate the request
    Then validation errors should be returned
    And the error should indicate unsupported content type

  Scenario: Validate request with extra properties
    Given a request body with additional properties
    And the schema has "additionalProperties: false"
    When I validate the request
    Then validation errors should be returned
    And the error should indicate unexpected properties

  Scenario: Validate request headers
    Given a request with required headers
    When I validate the request
    Then header validation should be performed
    And missing or invalid headers should be reported

  Scenario: Validate valid response
    Given a valid 200 response for GET "/pets"
    When I validate the response
    Then no validation errors should be returned
    And the response should be marked as valid

  Scenario: Validate response with invalid status code
    Given a 299 response for an operation
    And the spec doesn't define 299 responses
    When I validate the response
    Then validation errors should be returned
    And the error should indicate unexpected status code

  Scenario: Validate response body against schema
    Given a response body
    When I validate it against the response schema
    Then schema compliance should be checked
    And any violations should be reported

  Scenario: Validate response with missing required fields
    Given a response missing required fields
    When I validate the response
    Then validation errors should be returned
    And missing fields should be listed

  Scenario: Validate response headers
    Given a response with headers
    When I validate the response
    Then response headers should be validated
    And header schema violations should be reported

  Scenario: Validate array response
    Given a response containing an array
    When I validate the response
    Then each array item should be validated
    And any invalid items should be reported

  Scenario: Validate nested object response
    Given a response with nested objects
    When I validate the response
    Then all nested properties should be validated
    And validation should recurse through the structure

  Scenario: Validate response with enum constraint violation
    Given a response with enum field containing invalid value
    When I validate the response
    Then validation errors should be returned
    And the error should indicate enum constraint violation

  Scenario: Validate response with pattern constraint
    Given a response with string not matching required pattern
    When I validate the response
    Then validation errors should be returned
    And the error should indicate pattern mismatch

  Scenario: Provide detailed error messages
    Given any validation error
    When the error is reported
    Then the error message should include the path to the invalid element
    And it should explain what validation rule was violated
    And it should suggest how to fix the error

  Scenario: Validate request with security requirements
    Given a request to a secured endpoint
    When I validate the request
    Then security requirements should be checked
    And missing authentication should be reported

  Scenario: Handle validation exceptions gracefully
    Given a malformed request that causes validation exception
    When I validate the request
    Then the exception should be caught
    And a user-friendly error should be returned
