Feature: Request Matching
  As a developer
  I want to match incoming requests to OpenAPI operations
  So that I can provide the appropriate mock response

  Background:
    Given a loaded OpenAPI specification with multiple endpoints

  Scenario: Match simple GET request
    Given a GET request to "/pets"
    When I match the request against the spec
    Then the correct operation should be identified
    And the operation ID should be "listPets"

  Scenario: Match request with path parameters
    Given a GET request to "/pets/123"
    When I match the request against the spec
    Then the correct operation should be identified
    And path parameter "petId" should equal "123"

  Scenario: Match request with multiple path parameters
    Given a GET request to "/users/42/posts/99"
    When I match the request against the spec
    Then the correct operation should be identified
    And path parameter "userId" should equal "42"
    And path parameter "postId" should equal "99"

  Scenario: Match POST request with body
    Given a POST request to "/pets" with JSON body
    When I match the request against the spec
    Then the correct operation should be identified
    And the request body should be accessible

  Scenario: Match request with query parameters
    Given a GET request to "/pets?limit=10&offset=20"
    When I match the request against the spec
    Then the correct operation should be identified
    And query parameter "limit" should equal "10"
    And query parameter "offset" should equal "20"

  Scenario: No match for undefined path
    Given a GET request to "/undefined/path"
    When I match the request against the spec
    Then no operation should be matched
    And None should be returned

  Scenario: No match for undefined method
    Given a PATCH request to "/pets"
    And the spec only defines GET and POST for "/pets"
    When I match the request against the spec
    Then no operation should be matched
    And None should be returned

  Scenario: Match request with special characters in path
    Given a GET request to "/items/foo%20bar"
    When I match the request against the spec
    Then the correct operation should be identified
    And path parameter should be properly URL decoded

  Scenario: Build URL map from OpenAPI paths
    Given an OpenAPI spec with various path patterns
    When the URL map is built
    Then all paths should be converted to Werkzeug format
    And OpenAPI parameters should become Werkzeug variables

  Scenario: Match request with headers
    Given a GET request with custom headers
    When I match the request against the spec
    Then the operation should be identified
    And request headers should be accessible

  Scenario: Case-insensitive method matching
    Given a get request to "/pets" (lowercase method)
    When I match the request against the spec
    Then the correct operation should be identified
    And method matching should be case-insensitive

  Scenario: Match request with base URL
    Given a base URL "https://api.example.com"
    And a GET request to "https://api.example.com/pets"
    When I match the request against the spec
    Then the correct operation should be identified
    And the base URL should be properly handled

  Scenario: Match request with trailing slash
    Given a GET request to "/pets/"
    And the spec defines "/pets" without trailing slash
    When I match the request against the spec
    Then the correct operation should be identified
    And trailing slashes should be handled gracefully

  Scenario: Convert matches to OpenAPI request format
    Given a matched request
    When converting to OpenAPI request format
    Then an OpenAPIRequest object should be created
    And it should contain all request details
