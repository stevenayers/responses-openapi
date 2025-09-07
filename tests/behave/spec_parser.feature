Feature: OpenAPI Specification Parser
  As a developer
  I want to parse OpenAPI specifications
  So that I can use them to generate mock responses

  Scenario: Parse valid OpenAPI 3.0 YAML specification
    Given an OpenAPI 3.0 specification in YAML format
    When I load the specification
    Then the spec should be parsed successfully
    And the spec object should contain all paths
    And the spec object should contain all operations

  Scenario: Parse valid OpenAPI 3.0 JSON specification
    Given an OpenAPI 3.0 specification in JSON format
    When I load the specification
    Then the spec should be parsed successfully
    And the spec object should contain all paths
    And the spec object should contain all operations

  Scenario: Parse OpenAPI 3.1 specification
    Given an OpenAPI 3.1 specification
    When I load the specification
    Then the spec should be parsed successfully
    And OpenAPI 3.1 features should be supported

  Scenario: Cache parsed specifications
    Given a previously parsed specification
    When I load the same specification again
    Then the cached version should be returned
    And no re-parsing should occur

  Scenario: Handle invalid OpenAPI specification
    Given an invalid OpenAPI specification
    When I attempt to load the specification
    Then a validation error should be raised
    And the error should indicate what is invalid

  Scenario: Parse specification with $ref references
    Given a specification with $ref references
    When I load the specification
    Then all references should be resolved
    And the resolved spec should be complete

  Scenario: Parse specification with external references
    Given a specification with external file references
    When I load the specification
    Then external references should be resolved
    And the complete spec should be available

  Scenario: Get operation by path and method
    Given a loaded OpenAPI specification
    When I request an operation by path "/pets" and method "GET"
    Then the correct operation should be returned
    And it should contain operation details like parameters and responses

  Scenario: Get non-existent operation
    Given a loaded OpenAPI specification
    When I request a non-existent operation
    Then None should be returned
    And no error should be raised

  Scenario: Access request and response validators
    Given a loaded OpenAPI specification
    When I access the validators
    Then a request validator should be available
    And a response validator should be available

  Scenario: Parse specification from URL
    Given an OpenAPI specification URL
    When I load the specification from URL
    Then the spec should be downloaded and parsed
    And it should be cached for future use

  Scenario: Handle circular references
    Given a specification with circular references
    When I load the specification
    Then circular references should be handled gracefully
    And the spec should be usable

  Scenario: Parse specification with components
    Given a specification with reusable components
    When I load the specification
    Then all components should be accessible
    And components should be properly referenced in operations

  Scenario: Validate spec against OpenAPI schema
    Given any OpenAPI specification
    When it is loaded
    Then it should be validated against the OpenAPI schema
    And only valid specs should be accepted
