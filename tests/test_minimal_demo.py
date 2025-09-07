"""
Minimal demonstration of responses-openapi functionality.

This test shows the basic end-to-end functionality of mocking
HTTP responses based on an OpenAPI specification.
"""
import json

import pytest
import requests
from responses_openapi import OpenAPIMocker


def test_basic_mocking_with_context_manager():
    """Test basic mocking using context manager."""
    # Create mocker with the official Petstore spec
    with OpenAPIMocker('tests/fixtures/petstore.yaml', base_url='https://petstore3.swagger.io/api/v3') as mocker:
        # Make a request to a mocked endpoint
        response = requests.get('https://petstore3.swagger.io/api/v3/pet/123')

        # The response should be mocked
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

        # Should have generated data from the Pet schema
        assert 'id' in data
        assert 'name' in data
        print(f"Mocked response: {json.dumps(data, indent=2)}")


@pytest.mark.openapi_mock(spec='tests/fixtures/petstore.yaml', base_url='https://petstore3.swagger.io/api/v3')
def test_with_pytest_marker():
    """Test using pytest marker for automatic mocking."""
    # The marker automatically sets up mocking
    response = requests.get('https://petstore3.swagger.io/api/v3/pet/findByStatus?status=available')

    assert response.status_code == 200
    data = response.json()

    # Should return an array of pets
    assert isinstance(data, list)
    if data:  # If we generated items
        assert 'id' in data[0]
        assert 'name' in data[0]
    print(f"Mocked findByStatus response: {json.dumps(data, indent=2)}")


def test_with_fixture(openapi_mocker):
    """Test using the openapi_mocker fixture."""
    # Load spec using the fixture
    openapi_mocker.load_spec('tests/fixtures/petstore.yaml')

    # Need to reload spec with base_url - update the mocker's registered routes
    openapi_mocker.options['base_url'] = 'https://petstore3.swagger.io/api/v3'
    openapi_mocker._register_routes()  # Re-register with new base URL

    with openapi_mocker:
        # Test POST endpoint
        response = requests.post(
            'https://petstore3.swagger.io/api/v3/pet',
            json={'name': 'Fluffy', 'status': 'available'}
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        print(f"Mocked POST response: {json.dumps(data, indent=2)}")
