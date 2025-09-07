"""
Utility functions for Behave step definitions.

Provides common functionality for loading and working with
OpenAPI specifications in tests.
"""

from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import json


def load_fixture_spec(spec_name: str) -> tuple[Path, Dict[str, Any]]:
    """
    Load an OpenAPI specification fixture file.

    :param spec_name: Name of the spec file (without path)
    :type spec_name: str
    :returns: Tuple of (file path, spec content as dict)
    :rtype: tuple[Path, Dict[str, Any]]
    :raises FileNotFoundError: If the spec file doesn't exist

    .. code-block:: python

        spec_path, spec_content = load_fixture_spec('petstore.yaml')
        print(spec_content['openapi'])  # '3.0.4'
    """
    fixtures_dir = Path(__file__).parent.parent / 'fixtures'
    spec_path = fixtures_dir / spec_name

    if not spec_path.exists():
        raise FileNotFoundError(f"Fixture spec not found: {spec_path}")

    with spec_path.open('r') as f:
        if spec_path.suffix in ['.yaml', '.yml']:
            content = yaml.safe_load(f)
        elif spec_path.suffix == '.json':
            content = json.load(f)
        else:
            raise ValueError(f"Unsupported spec format: {spec_path.suffix}")

    return spec_path, content


def get_fixtures_dir() -> Path:
    """
    Get the path to the fixtures directory.

    :returns: Path to the fixtures directory
    :rtype: Path
    """
    return Path(__file__).parent / 'fixtures'


def get_test_spec_path(spec_name: str) -> Path:
    """
    Get the full path to a test specification file.

    :param spec_name: Name of the spec file
    :type spec_name: str
    :returns: Full path to the spec file
    :rtype: Path
    """
    return get_fixtures_dir() / spec_name
