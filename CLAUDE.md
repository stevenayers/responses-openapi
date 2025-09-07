# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

`responses-openapi` is a pytest plugin that automatically generates HTTP mock responses from OpenAPI specifications. It builds on top of the `responses` library to provide seamless integration with existing test infrastructure while adding schema-driven mock generation.

## Development Commands

### Environment Setup
```bash
# Install dependencies using uv (package manager)
uv sync

# Activate virtual environment
source .venv/bin/activate
```

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_file.py

# Run with coverage
pytest --cov=src/responses_openapi

# Run with verbose output
pytest -v
```

### Code Quality
```bash
# Run linter
ruff check .

# Auto-fix linting issues
ruff check --fix .

# Format code
ruff format .
```

## Architecture

The project follows a modular architecture with the following core components:

1. **Plugin Manager** (`plugin.py`) - Pytest integration, manages lifecycle and configuration
2. **Spec Parser** (`parser.py`) - Loads and validates OpenAPI specs using `openapi-core`
3. **Request Matcher** (`matcher.py`) - Matches incoming requests to OpenAPI operations using werkzeug routing
4. **Response Generator** (`generator.py`) - Generates mock responses from schemas using hypothesis-jsonschema
5. **Schema Validator** (`validator.py`) - Validates requests/responses against OpenAPI schemas
6. **Core Mocker** (`core.py`) - Main orchestrator integrating all components with the responses library

## Key Dependencies

- **responses** - HTTP mocking library (foundation)
- **openapi-core** - OpenAPI parsing, validation, and request/response handling
- **pytest** - Testing framework integration
- **werkzeug** - URL routing and request matching
- **hypothesis-jsonschema** - Generate test data from JSON schemas
- **faker** - Realistic fake data generation

## Implementation Notes

- The project leverages `openapi-core` extensively for OpenAPI spec parsing, validation, and schema handling
- Request matching uses werkzeug's routing system to convert OpenAPI paths to regex patterns
- Response generation prioritizes examples from the spec, falling back to hypothesis-jsonschema for automatic generation
- All components are designed to work with the existing `responses` library infrastructure
- The plugin supports both marker-based (`@pytest.mark.openapi_mock`) and fixture-based usage patterns

## Testing Strategy

When implementing features:
1. Create unit tests for individual components in isolation
2. Add integration tests for component interactions
3. Include end-to-end tests with real OpenAPI specs (e.g., Petstore)
4. Ensure all tests pass before committing changes