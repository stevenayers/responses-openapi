# responses-openapi Design Document

## Project Overview

`responses-openapi` is a pytest plugin that automatically generates HTTP mock responses from OpenAPI specifications. It builds on top of the `responses` library to provide seamless integration with existing test infrastructure while adding the power of schema-driven mock generation.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────┐
│                    responses-openapi                   │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Plugin     │  │    Spec      │  │   Response   │  │
│  │   Manager    │  │    Parser    │  │  Generator   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                 │                   │          │
│         │                 ▼                   ▼          │
│         │          ┌──────────────┐   ┌──────────────┐  │
│         │          │ openapi-core │   │  hypothesis- │  │
│         │          │              │   │  jsonschema  │  │
│         │          └──────────────┘   └──────────────┘  │
│         │                                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Request    │  │   Schema     │  │    Faker     │  │
│  │   Matcher    │  │  Validator   │  │  Integration │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│         │                 │                   │          │
│         ▼                 ▼                   ▼          │
│  ┌──────────────────────────────────────────────────┐   │
│  │            openapi-core + werkzeug               │   │
│  └──────────────────────────────────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    responses library    │
              └─────────────────────────┘
```

### Component Descriptions

#### 1. Plugin Manager (`plugin.py`)
- **Purpose**: Main entry point for pytest integration
- **Responsibilities**:
  - Register pytest hooks and fixtures
  - Manage plugin lifecycle
  - Handle configuration from pytest.ini and environment variables
  - Provide pytest markers (`@pytest.mark.openapi_mock`)

```python
# plugin.py
import pytest
from typing import Optional
from .core import OpenAPIMocker

def pytest_configure(config):
    """Register the openapi_mock marker."""
    config.addinivalue_line(
        "markers", 
        "openapi_mock(spec, **options): mark test to use OpenAPI mocking"
    )

@pytest.fixture
def openapi_mocker():
    """Fixture providing OpenAPIMocker instance."""
    mocker = OpenAPIMocker()
    yield mocker
    mocker.cleanup()

def pytest_runtest_setup(item):
    """Set up OpenAPI mocking for marked tests."""
    marker = item.get_closest_marker("openapi_mock")
    if marker:
        spec = marker.kwargs.get("spec")
        mocker = OpenAPIMocker(spec, **marker.kwargs)
        mocker.start()
        item._openapi_mocker = mocker
```

#### 2. Spec Parser (`parser.py`)
- **Purpose**: Parse and validate OpenAPI specifications using existing libraries
- **Responsibilities**:
  - Load OpenAPI specs from files or URLs
  - Leverage `openapi-core` for parsing and validation
  - Provide convenient access to operations and schemas
  - Cache parsed specifications

```python
# parser.py
from typing import Dict, Any, Optional
from functools import lru_cache
from openapi_core import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator
from openapi_schema_validator import validate
import yaml
import json
from pathlib import Path

class SpecParser:
    def __init__(self):
        self.spec_cache = {}
        self.validators_cache = {}
        
    @lru_cache(maxsize=10)
    def load_spec(self, spec_path: str) -> Spec:
        """Load and parse OpenAPI specification using openapi-core."""
        if spec_path in self.spec_cache:
            return self.spec_cache[spec_path]
            
        # Load raw spec
        with open(spec_path, 'r') as f:
            if spec_path.endswith('.yaml') or spec_path.endswith('.yml'):
                spec_dict = yaml.safe_load(f)
            else:
                spec_dict = json.load(f)
        
        # Validate spec against OpenAPI schema
        validate(spec_dict)
        
        # Create openapi-core Spec object (handles $ref resolution automatically)
        spec = Spec.from_dict(spec_dict)
        
        # Cache spec and validators
        self.spec_cache[spec_path] = spec
        self.validators_cache[spec_path] = {
            'request': openapi_request_validator(spec),
            'response': openapi_response_validator(spec)
        }
        
        return spec
        
    def get_operation(self, spec: Spec, method: str, path: str) -> Optional[Any]:
        """Get operation from spec using openapi-core."""
        try:
            return spec[path][method.lower()]
        except KeyError:
            return None
```

#### 3. Request Matcher (`matcher.py`)
- **Purpose**: Match incoming requests to OpenAPI operations
- **Responsibilities**:
  - Use `openapi-core` for request routing and matching
  - Extract and validate path parameters
  - Handle query parameters and request bodies

```python
# matcher.py
from typing import Optional, Dict, Any
from openapi_core import Spec
from openapi_core.contrib.requests import RequestsOpenAPIRequest
from openapi_core.validation.request import openapi_request_validator
from werkzeug.routing import Map, Rule
from werkzeug.datastructures import ImmutableMultiDict
from urllib.parse import urlparse, parse_qs

class RequestMatcher:
    def __init__(self, spec: Spec):
        self.spec = spec
        self.url_map = self._build_url_map()
        
    def _build_url_map(self) -> Map:
        """Build Werkzeug URL map from OpenAPI paths."""
        rules = []
        for path, path_item in self.spec.paths.items():
            # Convert OpenAPI path to Werkzeug format: {param} -> <param>
            werkzeug_path = path.replace('{', '<').replace('}', '>')
            for method in path_item.operations:
                rules.append(Rule(werkzeug_path, endpoint=f"{method}:{path}", methods=[method.upper()]))
        return Map(rules)
        
    def match_request(self, request) -> Optional[Dict[str, Any]]:
        """Match a request to an OpenAPI operation using openapi-core."""
        # Convert to OpenAPI request
        openapi_request = RequestsOpenAPIRequest(request)
        
        # Find matching operation
        adapter = self.url_map.bind(request.host)
        try:
            endpoint, path_params = adapter.match(request.path, method=request.method)
            method, openapi_path = endpoint.split(':', 1)
            
            return {
                'operation': self.spec[openapi_path][method.lower()],
                'path': openapi_path,
                'path_params': path_params,
                'openapi_request': openapi_request
            }
        except Exception:
            return None
```

#### 4. Response Generator (`generator.py`)
- **Purpose**: Generate mock responses from OpenAPI schemas
- **Responsibilities**:
  - Use `openapi-core` schemas with `jsonschema-faker` or `hypothesis-jsonschema`
  - Leverage examples from the spec when available
  - Generate realistic fake data using Faker
  - Handle different content types and headers

```python
# generator.py
from typing import Any, Dict, Optional
from faker import Faker
from openapi_core import Spec
from openapi_core.schemas import Schema
from hypothesis import strategies as st
from hypothesis_jsonschema import from_schema
import json

class ResponseGenerator:
    def __init__(self, spec: Spec, faker_locale: str = "en_US"):
        self.spec = spec
        self.faker = Faker(faker_locale)
        
    def generate_response(self, operation: Any, status_code: int = 200) -> Dict[str, Any]:
        """Generate a mock response for an operation using openapi-core schemas."""
        response_spec = operation.responses.get(str(status_code), operation.responses.get("default"))
        
        if not response_spec:
            return {"status": status_code}
            
        # Get content from openapi-core response object
        content = response_spec.content
        
        # Prefer JSON responses
        if "application/json" in content:
            media_type = content["application/json"]
            
            # Use example if available
            if media_type.example is not None:
                body = media_type.example
            elif media_type.examples:
                # Use first example from examples dict
                first_example = next(iter(media_type.examples.values()))
                body = first_example.value
            else:
                # Generate from schema using hypothesis-jsonschema
                schema = media_type.schema
                if schema:
                    # Convert openapi-core schema to dict for hypothesis
                    schema_dict = self._schema_to_dict(schema)
                    strategy = from_schema(schema_dict)
                    body = strategy.example()
                else:
                    body = {}
                
            # Extract headers from response spec
            headers = {}
            if response_spec.headers:
                for header_name, header_spec in response_spec.headers.items():
                    if header_spec.example:
                        headers[header_name] = str(header_spec.example)
                    elif header_spec.schema:
                        # Generate header value from schema
                        headers[header_name] = str(self._generate_simple_value(header_spec.schema))
                        
            return {
                "json": body,
                "status": status_code,
                "headers": headers
            }
            
    def _schema_to_dict(self, schema: Schema) -> Dict[str, Any]:
        """Convert openapi-core Schema object to dict for hypothesis."""
        # This would extract the raw schema dict from openapi-core's Schema object
        # The actual implementation depends on openapi-core's internal structure
        return schema.raw  # or schema.__dict__ depending on the version
        
    def _generate_simple_value(self, schema: Schema) -> Any:
        """Generate a simple value for headers based on schema."""
        if schema.enum:
            return self.faker.random_element(schema.enum)
        elif schema.type == "string":
            if schema.format == "date":
                return self.faker.date()
            elif schema.format == "date-time":
                return self.faker.iso8601()
            else:
                return self.faker.word()
        elif schema.type == "integer":
            return self.faker.random_int()
        elif schema.type == "number":
            return self.faker.random_number()
        elif schema.type == "boolean":
            return self.faker.boolean()
        return "default"
```

#### 5. Schema Validator (`validator.py`)
- **Purpose**: Validate requests and responses using openapi-core validators
- **Responsibilities**:
  - Leverage `openapi-core` validation capabilities
  - Provide detailed validation error messages
  - Support both request and response validation

```python
# validator.py
from typing import List, Optional
from openapi_core import Spec
from openapi_core.validation.request import openapi_request_validator
from openapi_core.validation.response import openapi_response_validator
from openapi_core.validation.request.datatypes import OpenAPIRequest
from openapi_core.validation.response.datatypes import OpenAPIResponse
from openapi_core.exceptions import OpenAPIError

class SchemaValidator:
    def __init__(self, spec: Spec):
        self.spec = spec
        self.request_validator = openapi_request_validator(spec)
        self.response_validator = openapi_response_validator(spec)
        
    def validate_request(self, openapi_request: OpenAPIRequest) -> List[str]:
        """Validate request using openapi-core."""
        errors = []
        
        try:
            # openapi-core handles all validation including:
            # - path parameters
            # - query parameters
            # - headers
            # - request body
            # - content type
            result = self.request_validator.validate(openapi_request)
            
            # Check for validation errors
            if result.errors:
                for error in result.errors:
                    errors.append(str(error))
                    
        except OpenAPIError as e:
            errors.append(f"Request validation error: {str(e)}")
            
        return errors
        
    def validate_response(self, openapi_request: OpenAPIRequest, openapi_response: OpenAPIResponse) -> List[str]:
        """Validate response using openapi-core."""
        errors = []
        
        try:
            # openapi-core validates:
            # - response status code
            # - response headers
            # - response body against schema
            # - content type
            result = self.response_validator.validate(openapi_request, openapi_response)
            
            if result.errors:
                for error in result.errors:
                    errors.append(str(error))
                    
        except OpenAPIError as e:
            errors.append(f"Response validation error: {str(e)}")
            
        return errors
```

#### 6. Core Mocker (`core.py`)
- **Purpose**: Main orchestrator that ties all components together
- **Responsibilities**:
  - Coordinate between parser, matcher, generator, and validator
  - Integrate with responses library
  - Provide high-level API for test usage
  - Handle context management

```python
# core.py
import responses
import re
import json
from typing import Optional, Dict, Any
from openapi_core import Spec
from openapi_core.contrib.requests import RequestsOpenAPIRequest, RequestsOpenAPIResponse
from .parser import SpecParser
from .matcher import RequestMatcher
from .generator import ResponseGenerator
from .validator import SchemaValidator

class OpenAPIMocker:
    def __init__(self, spec_path: Optional[str] = None, **options):
        self.parser = SpecParser()
        self.spec = None
        self.generator = None
        self.matcher = None
        self.validator = None
        self.options = options
        self.responses_mock = responses.RequestsMock()
        self.overrides = {}
        
        if spec_path:
            self.load_spec(spec_path)
            
    def load_spec(self, spec_path: str):
        """Load OpenAPI specification."""
        self.spec = self.parser.load_spec(spec_path)
        self.generator = ResponseGenerator(self.spec, self.options.get("faker_locale", "en_US"))
        self.matcher = RequestMatcher(self.spec)
        self.validator = SchemaValidator(self.spec)
        self._register_routes()
        
    def _register_routes(self):
        """Register all routes from OpenAPI spec with responses."""
        for path, path_item in self.spec.paths.items():
            for method in path_item.operations:
                operation = path_item.operations[method]
                self._register_operation(method.upper(), path, operation)
                    
    def _register_operation(self, method: str, path: str, operation: Any):
        """Register a single operation with responses."""
        def callback(request):
            # Check for overrides
            override_key = f"{method}:{path}"
            if override_key in self.overrides:
                return self.overrides[override_key]
                
            # Convert to OpenAPI request for validation
            openapi_request = RequestsOpenAPIRequest(request)
            
            # Validate request if enabled
            if self.options.get("validate_requests"):
                errors = self.validator.validate_request(openapi_request)
                if errors:
                    return (400, {}, json.dumps({"errors": errors}))
                    
            # Generate response
            response_data = self.generator.generate_response(operation)
            
            # Validate response if enabled
            if self.options.get("validate_responses"):
                # Create OpenAPI response for validation
                openapi_response = RequestsOpenAPIResponse(
                    status_code=response_data["status"],
                    headers=response_data.get("headers", {}),
                    data=json.dumps(response_data.get("json"))
                )
                errors = self.validator.validate_response(openapi_request, openapi_response)
                if errors:
                    raise ValueError(f"Generated invalid response: {errors}")
                    
            return (
                response_data["status"], 
                response_data.get("headers", {}), 
                json.dumps(response_data.get("json"))
            )
            
        # Convert OpenAPI path to regex pattern for responses
        # {param} -> (?P<param>[^/]+)
        regex_path = re.sub(r'\{([^}]+)\}', r'(?P<\1>[^/]+)', path)
        
        # Build full URL pattern
        base_url = self.options.get("base_url", "")
        if base_url:
            full_pattern = f"{base_url.rstrip('/')}{regex_path}"
        else:
            full_pattern = f".*{regex_path}"
            
        self.responses_mock.add_callback(
            method,
            re.compile(full_pattern),
            callback=callback
        )
        
    def override(self, method: str, path: str, **response_kwargs):
        """Override a specific endpoint's response."""
        self.overrides[f"{method}:{path}"] = response_kwargs
        
    def set_response_code(self, method: str, path: str, status_code: int):
        """Set specific status code for an endpoint."""
        operation = self.spec.paths[path].operations[method.lower()]
        response_data = self.generator.generate_response(operation, status_code)
        self.overrides[f"{method}:{path}"] = (
            status_code,
            response_data.get("headers", {}),
            json.dumps(response_data.get("json"))
        )
        
    def __enter__(self):
        """Start mocking."""
        self.responses_mock.start()
        return self
        
    def __exit__(self, *args):
        """Stop mocking."""
        self.responses_mock.stop()
        self.responses_mock.reset()
        
    def cleanup(self):
        """Clean up resources."""
        self.responses_mock.reset()
```

## Implementation Phases

### Phase 1: Core Functionality (MVP)
- Basic OpenAPI 3.0 parsing
- Simple response generation from schemas
- Integration with responses library
- Basic pytest plugin setup
- Support for JSON responses only

### Phase 2: Enhanced Features
- Full OpenAPI 3.0 and 3.1 support
- Request validation
- Response validation
- Support for all content types
- Example usage from spec
- Parameter extraction and validation

### Phase 3: Advanced Capabilities
- Faker integration for realistic data
- Support for `allOf`, `oneOf`, `anyOf`
- Circular reference handling
- Performance optimizations (caching, lazy loading)
- Custom faker providers for domain-specific data

### Phase 4: Developer Experience
- Detailed error messages
- Debug mode with request/response logging
- CLI tool for testing specs
- VSCode/PyCharm integration
- Comprehensive documentation

## Testing Strategy

### Unit Tests
- Test each component in isolation
- Mock dependencies appropriately
- Cover edge cases and error conditions

### Integration Tests
- Test component interactions
- Test with real OpenAPI specs (Petstore, etc.)
- Test pytest integration

### End-to-End Tests
- Test complete workflows
- Test with various OpenAPI spec versions
- Performance benchmarks

## Dependencies

### Core Dependencies
- `responses` >= 0.20.0 - HTTP mocking library
- `openapi-core` >= 0.18.0 - OpenAPI spec parsing, validation, and request/response handling
- `openapi-schema-validator` >= 0.6.0 - OpenAPI schema validation
- `pyyaml` >= 6.0 - YAML parsing for OpenAPI specs
- `pytest` >= 7.0 - Testing framework
- `werkzeug` >= 2.0 - URL routing and matching

### Optional Dependencies
- `faker` >= 18.0 - Realistic fake data generation
- `hypothesis-jsonschema` >= 0.22.0 - Generate test data from JSON schemas
- `prance` >= 23.0 - Alternative OpenAPI parser with built-in reference resolution

## Configuration Options

```python
# Configuration structure
{
    "spec": str,                      # Path to OpenAPI spec
    "base_url": str,                  # Base URL for the API
    "validate_requests": bool,        # Enable request validation
    "validate_responses": bool,       # Enable response validation
    "faker_locale": str,             # Locale for Faker
    "strict_mode": bool,             # Fail on any validation error
    "use_examples": bool,            # Prefer examples over generated data
    "cache_specs": bool,             # Cache parsed specifications
    "debug": bool,                   # Enable debug logging
}
```

## Error Handling

### Validation Errors
- Clear error messages indicating what failed validation
- Include path to the failing element
- Suggest fixes where possible

### Spec Parsing Errors
- Indicate invalid OpenAPI spec format
- Point to specific line/element that's invalid
- Fallback to partial functionality where possible

### Runtime Errors
- Graceful degradation
- Informative error messages
- Debug mode for detailed tracing

## Performance Considerations

### Spec Parsing
- Cache parsed specs across test runs
- Lazy load spec sections as needed
- Pre-compile regex patterns

### Response Generation
- Cache generated responses for identical schemas
- Optimize faker calls
- Use connection pooling for external spec fetching

### Memory Management
- Clear caches between test sessions
- Limit cache sizes
- Stream large responses

## Security Considerations

- Validate external spec URLs
- Sanitize generated data
- Prevent arbitrary code execution through specs
- Limit resource consumption (memory, CPU)

## Future Enhancements

### Potential Features
- GraphQL support
- gRPC support
- WebSocket mocking
- Record and replay mode
- Spec generation from tests
- Integration with other mocking libraries
- Multi-spec support (microservices)
- Contract testing capabilities

### Ecosystem Integration
- Integration with popular API clients (httpx, aiohttp)
- Integration with API documentation tools
- CI/CD pipeline integration
- Cloud testing platform support

## Conclusion

`responses-openapi` aims to bridge the gap between API specifications and testing by providing automatic, specification-driven mock generation. By building on top of the robust `responses` library and integrating seamlessly with pytest, it offers a powerful yet simple solution for API testing.