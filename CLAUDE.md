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
behave

# Run specific feature file
behave features/feature_name.feature

# Run with specific tags
behave --tags=@tag_name

# Run with verbose output
behave -v

# Run and stop on first failure
behave --stop
```

### Code Quality
```bash
# Run linter
uv run ruff check .

# Auto-fix linting issues
uv run ruff check --fix .

# Format code
uv run ruff format .

# Check formatting without applying changes
uv run ruff format --check .

# Run type checking
uv run mypy src/

# Run security checks
uv run bandit -r src/
uv run safety check

# Run coverage report
uv run coverage run --source=src -m behave
uv run coverage report
uv run coverage xml

# Run pre-commit hooks on all files
pre-commit run --all-files

# Install pre-commit hooks
pre-commit install
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

The project uses Behave for BDD (Behavior-Driven Development) testing. When implementing features:
1. Write feature files in Gherkin syntax describing the behavior
2. Implement step definitions for the scenarios
3. Create unit tests for individual components in isolation
4. Add integration tests for component interactions
5. Include end-to-end tests with real OpenAPI specs (e.g., Petstore)
6. Ensure all tests pass before committing changes
