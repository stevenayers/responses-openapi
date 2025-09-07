"""
Pytest plugin for OpenAPI mocking.

Provides pytest markers and fixtures for easy integration
of OpenAPI-based HTTP mocking in tests.
"""

from typing import Any, Generator

import pytest

from .core import OpenAPIMocker


def pytest_configure(config: Any) -> None:
    """
    Register the openapi_mock marker with pytest.

    :param config: Pytest configuration object
    :type config: Any
    """
    config.addinivalue_line("markers", "openapi_mock(spec, **options): mark test to use OpenAPI mocking")


@pytest.fixture
def openapi_mocker() -> Generator[OpenAPIMocker, None, None]:
    """
    Pytest fixture providing an OpenAPIMocker instance.

    :returns: OpenAPIMocker instance
    :rtype: Generator[OpenAPIMocker, None, None]

    .. code-block:: python

        def test_api(openapi_mocker):
            openapi_mocker.load_spec('petstore.yaml')
            with openapi_mocker:
                # Make mocked requests
                pass
    """
    mocker = OpenAPIMocker()
    yield mocker
    mocker.cleanup()


def pytest_runtest_setup(item: Any) -> None:
    """
    Set up OpenAPI mocking for tests marked with openapi_mock.

    :param item: Pytest test item
    :type item: Any
    """
    marker = item.get_closest_marker("openapi_mock")
    if marker:
        spec = marker.kwargs.get("spec")
        if not spec:
            raise ValueError("openapi_mock marker requires 'spec' argument")

        mocker = OpenAPIMocker(spec, **marker.kwargs)
        mocker.start()
        item._openapi_mocker = mocker


def pytest_runtest_teardown(item: Any) -> None:
    """
    Clean up OpenAPI mocking after test execution.

    :param item: Pytest test item
    :type item: Any
    """
    if hasattr(item, "_openapi_mocker"):
        item._openapi_mocker.stop()
        item._openapi_mocker.cleanup()
        delattr(item, "_openapi_mocker")
