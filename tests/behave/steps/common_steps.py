"""
Common step definitions shared across multiple features.

These steps provide common functionality for all test scenarios.
"""

from typing import Any, Dict, Optional, List
from unittest.mock import Mock, MagicMock, patch
from behave import given, when, then
from pathlib import Path
import tempfile
import json
import yaml
from .utils import load_fixture_spec, get_test_spec_path


@given("a loaded OpenAPI specification with multiple endpoints")
def step_given_loaded_spec_multiple_endpoints(context: Any) -> None:
    """
    Create and load a spec with multiple endpoints.

    :param context: Behave context object
    :type context: Any
    """
    # Use the official petstore spec which has many endpoints
    spec_path, spec_content = load_fixture_spec('petstore.yaml')
    context.spec_file = str(spec_path)
    context.spec_content = spec_content

    from responses_openapi.parser import SpecParser
    context.parser = SpecParser()
    context.spec = context.parser.load_spec(context.spec_file)


@given("a response generator initialized with the spec")
def step_given_response_generator(context: Any) -> None:
    """
    Initialize a response generator with the spec.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.generator import ResponseGenerator
    context.generator = ResponseGenerator(context.spec)


@given("a schema validator initialized with the spec")
def step_given_schema_validator(context: Any) -> None:
    """
    Initialize a schema validator with the spec.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.validator import SchemaValidator
    context.validator = SchemaValidator(context.spec)


@given("an OpenAPIMocker instance")
def step_given_openapi_mocker(context: Any) -> None:
    """
    Create an OpenAPIMocker instance.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.core import OpenAPIMocker
    context.mocker = OpenAPIMocker()


@when("I validate the request")
def step_when_validate_request(context: Any) -> None:
    """
    Validate the current request.

    :param context: Behave context object
    :type context: Any
    """
    context.validation_errors = context.validator.validate_request(context.request)


@when("I validate the response")
def step_when_validate_response(context: Any) -> None:
    """
    Validate the current response.

    :param context: Behave context object
    :type context: Any
    """
    context.validation_errors = context.validator.validate_response(
        context.request, context.response
    )


@when("I generate a response")
def step_when_generate_response(context: Any) -> None:
    """
    Generate a response.

    :param context: Behave context object
    :type context: Any
    """
    context.generated_response = context.generator.generate_response(
        context.operation,
        getattr(context, 'status_code', 200)
    )


@then("validation errors should be returned")
def step_then_validation_errors_returned(context: Any) -> None:
    """
    Verify validation errors were returned.

    :param context: Behave context object
    :type context: Any
    """
    assert context.validation_errors is not None
    assert len(context.validation_errors) > 0


@then("no validation errors should be returned")
def step_then_no_validation_errors(context: Any) -> None:
    """
    Verify no validation errors were returned.

    :param context: Behave context object
    :type context: Any
    """
    assert context.validation_errors is not None
    assert len(context.validation_errors) == 0
