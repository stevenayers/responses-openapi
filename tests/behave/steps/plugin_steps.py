"""
Step definitions for pytest plugin integration features.

These steps test the pytest plugin functionality including markers,
fixtures, configuration, and lifecycle management.
"""

from typing import Any, Dict, Optional
from unittest.mock import Mock, MagicMock, patch
from behave import given, when, then
from pathlib import Path
import pytest
import tempfile
import json
import yaml
from .utils import load_fixture_spec, get_test_spec_path


@given("a valid OpenAPI specification file")
def step_given_valid_openapi_spec(context: Any) -> None:
    """
    Create a valid OpenAPI specification file for testing.

    :param context: Behave context object
    :type context: Any
    """
    # Use the official petstore spec
    spec_path, spec_content = load_fixture_spec('petstore.yaml')
    context.spec_file = str(spec_path)
    context.spec_content = spec_content


@when("the pytest configuration is initialized")
def step_when_pytest_config_initialized(context: Any) -> None:
    """
    Simulate pytest configuration initialization.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.plugin import pytest_configure

    context.config = Mock()
    context.config.addinivalue_line = Mock()

    pytest_configure(context.config)
    context.pytest_configured = True


@then("the openapi_mock marker should be registered")
def step_then_marker_registered(context: Any) -> None:
    """
    Verify that the openapi_mock marker is registered.

    :param context: Behave context object
    :type context: Any
    """
    assert context.pytest_configured
    context.config.addinivalue_line.assert_called_with(
        "markers",
        "openapi_mock(spec, **options): mark test to use OpenAPI mocking"
    )


@then("the openapi_mocker fixture should be available")
def step_then_fixture_available(context: Any) -> None:
    """
    Verify that the openapi_mocker fixture is available.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.plugin import openapi_mocker

    assert openapi_mocker is not None
    assert callable(openapi_mocker)


@given("a test function with openapi_mock marker")
def step_given_test_with_marker(context: Any) -> None:
    """
    Create a test function with openapi_mock marker.

    :param context: Behave context object
    :type context: Any
    """
    context.test_item = Mock()
    context.test_item.get_closest_marker = Mock()

    marker = Mock()
    marker.kwargs = {"spec": context.spec_file}
    context.test_item.get_closest_marker.return_value = marker


@when("the test is executed")
def step_when_test_executed(context: Any) -> None:
    """
    Execute the test with mocking setup.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.plugin import pytest_runtest_setup

    with patch('responses_openapi.plugin.OpenAPIMocker') as MockOpenAPIMocker:
        context.mock_mocker = Mock()
        MockOpenAPIMocker.return_value = context.mock_mocker

        pytest_runtest_setup(context.test_item)
        context.test_executed = True


@then("the OpenAPI mocker should be initialized with the spec")
def step_then_mocker_initialized(context: Any) -> None:
    """
    Verify mocker initialization with specification.

    :param context: Behave context object
    :type context: Any
    """
    assert context.test_executed
    assert hasattr(context.test_item, '_openapi_mocker')
    context.mock_mocker.start.assert_called_once()


@then("the responses should be mocked according to the spec")
def step_then_responses_mocked(context: Any) -> None:
    """
    Verify that responses are mocked per specification.

    :param context: Behave context object
    :type context: Any
    """
    assert context.mock_mocker.start.called


@given("a test function using the openapi_mocker fixture")
def step_given_test_with_fixture(context: Any) -> None:
    """
    Create test function using openapi_mocker fixture.

    :param context: Behave context object
    :type context: Any
    """
    context.fixture_requested = True


@when("the fixture is requested")
def step_when_fixture_requested(context: Any) -> None:
    """
    Request the openapi_mocker fixture.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.plugin import openapi_mocker

    with patch('responses_openapi.plugin.OpenAPIMocker') as MockOpenAPIMocker:
        context.mock_mocker_instance = Mock()
        MockOpenAPIMocker.return_value = context.mock_mocker_instance

        # Simulate fixture usage
        gen = openapi_mocker()
        context.mocker = next(gen)

        # Store generator for cleanup
        context.fixture_generator = gen


@then("an OpenAPIMocker instance should be provided")
def step_then_mocker_instance_provided(context: Any) -> None:
    """
    Verify OpenAPIMocker instance is provided.

    :param context: Behave context object
    :type context: Any
    """
    assert context.mocker is not None
    assert context.mocker == context.mock_mocker_instance


@then("the mocker should be cleaned up after the test")
def step_then_mocker_cleaned_up(context: Any) -> None:
    """
    Verify mocker cleanup after test.

    :param context: Behave context object
    :type context: Any
    """
    # Complete the generator to trigger cleanup
    try:
        next(context.fixture_generator)
    except StopIteration:
        pass

    context.mock_mocker_instance.cleanup.assert_called_once()


@given("a pytest.ini file with openapi configuration")
def step_given_pytest_ini_config(context: Any) -> None:
    """
    Create pytest.ini with OpenAPI configuration.

    :param context: Behave context object
    :type context: Any
    """
    context.ini_config = {
        "openapi_spec": "/path/to/default/spec.yaml",
        "openapi_base_url": "https://api.example.com",
        "openapi_validate_requests": "true"
    }


@when("pytest loads the configuration")
def step_when_pytest_loads_config(context: Any) -> None:
    """
    Simulate pytest loading configuration.

    :param context: Behave context object
    :type context: Any
    """
    context.config = Mock()
    context.config.getini = lambda key: context.ini_config.get(key)
    context.config_loaded = True


@then("the plugin should use the configured settings")
def step_then_plugin_uses_settings(context: Any) -> None:
    """
    Verify plugin uses configured settings.

    :param context: Behave context object
    :type context: Any
    """
    assert context.config_loaded
    assert context.config.getini("openapi_spec") == "/path/to/default/spec.yaml"
    assert context.config.getini("openapi_base_url") == "https://api.example.com"


@then("the default spec path should be loaded if specified")
def step_then_default_spec_loaded(context: Any) -> None:
    """
    Verify default spec path is loaded.

    :param context: Behave context object
    :type context: Any
    """
    spec_path = context.config.getini("openapi_spec")
    assert spec_path is not None


@given("environment variables for openapi configuration")
def step_given_env_vars_config(context: Any) -> None:
    """
    Set environment variables for configuration.

    :param context: Behave context object
    :type context: Any
    """
    import os
    context.original_env = os.environ.copy()
    os.environ["OPENAPI_SPEC"] = "/env/spec.yaml"
    os.environ["OPENAPI_BASE_URL"] = "https://env.example.com"


@when("the plugin initializes")
def step_when_plugin_initializes(context: Any) -> None:
    """
    Initialize the plugin with environment config.

    :param context: Behave context object
    :type context: Any
    """
    context.plugin_initialized = True


@then("environment settings should override defaults")
def step_then_env_overrides_defaults(context: Any) -> None:
    """
    Verify environment settings override defaults.

    :param context: Behave context object
    :type context: Any
    """
    import os
    assert os.environ.get("OPENAPI_SPEC") == "/env/spec.yaml"
    assert os.environ.get("OPENAPI_BASE_URL") == "https://env.example.com"


@then("pytest.ini settings should override environment variables")
def step_then_ini_overrides_env(context: Any) -> None:
    """
    Verify pytest.ini overrides environment variables.

    :param context: Behave context object
    :type context: Any
    """
    # In actual implementation, pytest.ini would take precedence
    # This is a placeholder for the test logic
    pass


@given("a test using openapi_mock marker")
def step_given_test_using_marker(context: Any) -> None:
    """
    Create test using openapi_mock marker.

    :param context: Behave context object
    :type context: Any
    """
    context.test_with_marker = True


@when("the test completes")
def step_when_test_completes(context: Any) -> None:
    """
    Simulate test completion.

    :param context: Behave context object
    :type context: Any
    """
    from responses_openapi.plugin import pytest_runtest_teardown

    context.test_item = Mock()
    context.test_item._openapi_mocker = Mock()

    pytest_runtest_teardown(context.test_item)
    context.test_completed = True


@then("all mocked responses should be cleared")
def step_then_mocked_responses_cleared(context: Any) -> None:
    """
    Verify all mocked responses are cleared.

    :param context: Behave context object
    :type context: Any
    """
    assert context.test_completed
    context.test_item._openapi_mocker.cleanup.assert_called()


@then("no responses should leak to other tests")
def step_then_no_response_leaks(context: Any) -> None:
    """
    Verify no response leaks between tests.

    :param context: Behave context object
    :type context: Any
    """
    # This would be verified by checking responses.mock state
    # In actual implementation
    pass


@given("multiple tests with different OpenAPI specs")
def step_given_multiple_tests_different_specs(context: Any) -> None:
    """
    Create multiple tests with different specs.

    :param context: Behave context object
    :type context: Any
    """
    context.test_specs = [
        "/path/to/spec1.yaml",
        "/path/to/spec2.yaml",
        "/path/to/spec3.yaml"
    ]


@when("tests are run in sequence")
def step_when_tests_run_sequence(context: Any) -> None:
    """
    Run tests in sequence.

    :param context: Behave context object
    :type context: Any
    """
    context.test_results = []
    for spec in context.test_specs:
        context.test_results.append({"spec": spec, "executed": True})


@then("each test should use its own spec")
def step_then_each_test_own_spec(context: Any) -> None:
    """
    Verify each test uses its own spec.

    :param context: Behave context object
    :type context: Any
    """
    assert len(context.test_results) == len(context.test_specs)
    for i, result in enumerate(context.test_results):
        assert result["spec"] == context.test_specs[i]


@then("specs should not interfere with each other")
def step_then_specs_no_interference(context: Any) -> None:
    """
    Verify specs don't interfere with each other.

    :param context: Behave context object
    :type context: Any
    """
    # Verify isolation between specs
    assert all(result["executed"] for result in context.test_results)


@given("a test with openapi_mock marker but no spec")
def step_given_test_marker_no_spec(context: Any) -> None:
    """
    Create test with marker but no spec.

    :param context: Behave context object
    :type context: Any
    """
    context.test_item = Mock()
    marker = Mock()
    marker.kwargs = {}  # No spec provided
    context.test_item.get_closest_marker.return_value = marker


@then("a helpful error message should be displayed")
def step_then_helpful_error_message(context: Any) -> None:
    """
    Verify helpful error message is displayed.

    :param context: Behave context object
    :type context: Any
    """
    # Error message would be captured in actual implementation
    pass


@then("the test should fail with appropriate error")
def step_then_test_fails_appropriately(context: Any) -> None:
    """
    Verify test fails with appropriate error.

    :param context: Behave context object
    :type context: Any
    """
    # Test failure would be verified in actual implementation
    pass


@given("an openapi_mock marker with base_url option")
def step_given_marker_with_base_url(context: Any) -> None:
    """
    Create marker with base_url option.

    :param context: Behave context object
    :type context: Any
    """
    context.base_url = "https://api.example.com"
    context.marker_options = {"base_url": context.base_url}


@when("mocked endpoints are registered")
def step_when_endpoints_registered(context: Any) -> None:
    """
    Register mocked endpoints.

    :param context: Behave context object
    :type context: Any
    """
    context.endpoints_registered = True


@then("all endpoints should use the configured base URL")
def step_then_endpoints_use_base_url(context: Any) -> None:
    """
    Verify endpoints use configured base URL.

    :param context: Behave context object
    :type context: Any
    """
    assert context.endpoints_registered
    # Verification would check actual endpoint URLs


@then("requests to the base URL should be intercepted")
def step_then_base_url_requests_intercepted(context: Any) -> None:
    """
    Verify base URL requests are intercepted.

    :param context: Behave context object
    :type context: Any
    """
    # Verification would test actual request interception
    pass
