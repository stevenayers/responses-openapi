Feature: Response Generation
  As a developer
  I want to generate mock responses from OpenAPI schemas
  So that I can test my application with realistic data

  Background:
    Given a loaded OpenAPI specification
    And a response generator initialized with the spec

  Scenario: Generate response from simple schema
    Given an operation with a simple JSON response schema
    When I generate a response for status code 200
    Then a valid JSON response should be generated
    And the response should match the schema

  Scenario: Use example from specification
    Given an operation with an example response
    When I generate a response
    Then the example should be used as the response
    And no random data should be generated

  Scenario: Use examples from specification
    Given an operation with multiple examples
    When I generate a response
    Then one of the examples should be used
    And the example should be returned as-is

  Scenario: Generate response with nested objects
    Given a schema with nested object properties
    When I generate a response
    Then all nested objects should be populated
    And the structure should match the schema

  Scenario: Generate response with arrays
    Given a schema with array properties
    When I generate a response
    Then arrays should be generated with valid items
    And array items should match the item schema

  Scenario: Generate response for different status codes
    Given an operation with multiple response codes
    When I generate a response for status code 404
    Then the 404 response schema should be used
    And the response should match the 404 schema

  Scenario: Generate response with default status
    Given an operation with a "default" response
    When I generate a response for an undefined status code
    Then the default response schema should be used

  Scenario: Generate response with required fields
    Given a schema with required and optional fields
    When I generate a response
    Then all required fields should be present
    And optional fields may or may not be present

  Scenario: Generate response with enum values
    Given a schema with enum constraints
    When I generate a response
    Then enum fields should only contain allowed values
    And the values should be from the enum list

  Scenario: Generate response with format constraints
    Given a schema with format specifications
    When I generate a response with "date" format
    Then the field should contain a valid date
    When I generate a response with "email" format
    Then the field should contain a valid email
    When I generate a response with "uuid" format
    Then the field should contain a valid UUID

  Scenario: Generate response with Faker integration
    Given Faker is configured with locale "en_US"
    When I generate a response with string fields
    Then realistic fake data should be generated
    And the data should respect the locale setting

  Scenario: Generate response with allOf schema
    Given a schema using allOf composition
    When I generate a response
    Then the response should satisfy all schemas
    And properties from all schemas should be merged

  Scenario: Generate response with oneOf schema
    Given a schema using oneOf composition
    When I generate a response
    Then the response should match exactly one schema
    And the chosen schema should be valid

  Scenario: Generate response with anyOf schema
    Given a schema using anyOf composition
    When I generate a response
    Then the response should match at least one schema
    And all matching schemas should be valid

  Scenario: Generate response headers
    Given a response with defined headers
    When I generate a response
    Then response headers should be included
    And header values should match their schemas

  Scenario: Generate response with no schema
    Given an operation with no response schema
    When I generate a response
    Then a minimal response should be returned
    And the status code should be set correctly

  Scenario: Generate response for different content types
    Given an operation with multiple content types
    When I generate a response for "application/json"
    Then JSON response should be generated
    When I generate a response for "application/xml"
    Then the appropriate content type should be handled

  Scenario: Handle circular references in schema
    Given a schema with circular references
    When I generate a response
    Then the generation should complete successfully
    And circular references should be handled gracefully

  Scenario: Generate response with min/max constraints
    Given a schema with minimum and maximum values
    When I generate a response
    Then numeric values should respect min/max constraints
    And string lengths should respect minLength/maxLength
