# responses-openapi

A pytest plugin that automatically generates mock HTTP responses from OpenAPI specifications, built on top of the [responses](https://github.com/getsentry/responses) library.

## Overview

`responses-openapi` simplifies API testing by automatically creating mock responses based on your OpenAPI specification. Instead of manually defining mock responses for each test, you can leverage your existing OpenAPI spec to generate realistic, schema-compliant responses.

## Key Features

- 🚀 **Automatic Mock Generation**: Generate mock responses directly from OpenAPI 3.x specifications
- 🔧 **Built on `responses`**: Leverages the battle-tested `responses` library for HTTP mocking
- 📝 **Schema Validation**: Ensures mock responses comply with your OpenAPI schema
- 🎯 **Smart Example Usage**: Uses examples from your spec when available, falls back to realistic fake data
- 🔄 **Multiple Response Scenarios**: Support for different response codes and content types
- 🧪 **Pytest Integration**: Seamless integration with pytest fixtures and markers
- ⚡ **Performance**: Lazy loading and caching of OpenAPI specs for optimal test performance

## Installation

```bash
pip install responses-openapi
```

## Quick Start

### Basic Usage

```python
# test_api.py
import pytest
import requests

@pytest.mark.openapi_mock("petstore.yaml")
def test_get_pet():
    # The mock is automatically configured based on your OpenAPI spec
    response = requests.get("https://api.example.com/pets/123")
    
    assert response.status_code == 200
    assert "name" in response.json()
    assert "id" in response.json()
```

### Using Fixtures

```python
# conftest.py
import pytest
from pytest_openapi_mock import openapi_mocker

@pytest.fixture
def api_mock(openapi_mocker):
    openapi_mocker.load_spec("petstore.yaml")
    return openapi_mocker

# test_api.py
def test_create_pet(api_mock):
    with api_mock:
        response = requests.post(
            "https://api.example.com/pets",
            json={"name": "Fluffy", "type": "cat"}
        )
        
        assert response.status_code == 201
        assert response.json()["name"] == "Fluffy"
```

### Advanced Configuration

```python
@pytest.mark.openapi_mock(
    spec="api.yaml",
    base_url="https://api.example.com",
    validate_requests=True,  # Validate requests against schema
    validate_responses=True,  # Validate mock responses against schema
)
def test_api_with_validation():
    response = requests.get("https://api.example.com/users")
    assert response.status_code == 200
```

### Customizing Responses

```python
def test_custom_response(api_mock):
    # Override specific responses while keeping others auto-mocked
    api_mock.override(
        "GET", 
        "/pets/123",
        json={"id": 123, "name": "Custom Pet", "status": "sold"},
        status=200
    )
    
    with api_mock:
        response = requests.get("https://api.example.com/pets/123")
        assert response.json()["name"] == "Custom Pet"
```

### Testing Error Scenarios

```python
def test_error_response(api_mock):
    # Automatically use error responses defined in your OpenAPI spec
    api_mock.set_response_code("GET", "/pets/{petId}", 404)
    
    with api_mock:
        response = requests.get("https://api.example.com/pets/999")
        assert response.status_code == 404
        assert "error" in response.json()
```

## Configuration

### pytest.ini Options

```ini
[tool:pytest]
openapi_mock_spec_dir = ./specs  # Directory containing OpenAPI specs
openapi_mock_validate_requests = true  # Global request validation
openapi_mock_validate_responses = true  # Global response validation
openapi_mock_faker_locale = en_US  # Locale for generated fake data
```

### Environment Variables

```bash
OPENAPI_MOCK_SPEC_DIR=./specs
OPENAPI_MOCK_VALIDATE_REQUESTS=true
OPENAPI_MOCK_VALIDATE_RESPONSES=true
```

## How It Works

1. **Spec Loading**: The plugin loads and parses your OpenAPI specification
2. **Route Matching**: Incoming requests are matched against paths defined in the spec
3. **Response Generation**: Mock responses are generated based on:
   - Examples defined in the spec (highest priority)
   - Schema definitions with realistic fake data
   - Response headers and status codes from the spec
4. **Validation**: Optional validation ensures requests and responses comply with the schema

## Supported OpenAPI Features

- ✅ OpenAPI 3.0.x and 3.1.x
- ✅ Path parameters
- ✅ Query parameters
- ✅ Request body validation
- ✅ Multiple response codes
- ✅ Multiple content types
- ✅ Schema references (`$ref`)
- ✅ `allOf`, `oneOf`, `anyOf` schemas
- ✅ Example values
- ✅ Default values
- ✅ Enum constraints
- ✅ Format validation (email, uri, uuid, etc.)

## Integration with responses

Since `responses-openapi` is built on top of `responses`, you can use all the features of `responses` alongside the OpenAPI functionality:

```python
import responses

def test_mixed_mocking(api_mock):
    # Use OpenAPI mock for most endpoints
    with api_mock:
        # Add custom responses using standard responses decorators
        responses.add(
            responses.GET,
            "https://external-api.com/data",
            json={"custom": "data"},
            status=200
        )
        
        # Both OpenAPI mocks and custom mocks work together
        resp1 = requests.get("https://api.example.com/pets")  # OpenAPI mock
        resp2 = requests.get("https://external-api.com/data")  # Custom mock
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Acknowledgments

This project builds upon the excellent [responses](https://github.com/getsentry/responses) library by Sentry.