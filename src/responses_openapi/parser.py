"""
OpenAPI specification parser.

Handles loading and parsing of OpenAPI specifications.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


class SpecParser:
    """
    Parser for OpenAPI specifications.

    .. code-block:: python

        parser = SpecParser()
        spec = parser.load_spec('petstore.yaml')
    """

    def __init__(self) -> None:
        """
        Initialize the spec parser.
        """
        self.spec_cache: Dict[str, Any] = {}
        self.validators_cache: Dict[str, Dict[str, Any]] = {}

    def load_spec(self, spec_path: str) -> Dict[str, Any]:
        """
        Load and parse an OpenAPI specification.

        :param spec_path: Path to the specification file
        :type spec_path: str
        :returns: Parsed specification
        :rtype: Dict[str, Any]
        :raises FileNotFoundError: If spec file doesn't exist
        :raises ValueError: If spec is invalid
        """
        if spec_path in self.spec_cache:
            return self.spec_cache[spec_path]

        path = Path(spec_path)

        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        with path.open("r") as f:
            if path.suffix in [".yaml", ".yml"]:
                spec_dict = yaml.safe_load(f)
            elif path.suffix == ".json":
                spec_dict = json.load(f)
            else:
                raise ValueError(f"Unsupported spec format: {path.suffix}")

        # Basic validation
        if "openapi" not in spec_dict:
            raise ValueError("Invalid OpenAPI specification: missing 'openapi' field")

        # Create a simple spec object with paths attribute
        spec = type(
            "Spec",
            (),
            {"paths": spec_dict.get("paths", {}), "components": spec_dict.get("components", {}), "_raw": spec_dict},
        )()

        self.spec_cache[spec_path] = spec

        # Create stub validators
        self.validators_cache[spec_path] = {"request": None, "response": None}

        return spec

    def get_operation(self, spec: Any, method: str, path: str) -> Optional[Any]:
        """
        Get an operation from the spec by method and path.

        :param spec: OpenAPI specification
        :type spec: Any
        :param method: HTTP method
        :type method: str
        :param path: API path
        :type path: str
        :returns: Operation or None if not found
        :rtype: Optional[Any]
        """
        if hasattr(spec, "paths") and path in spec.paths:
            path_item = spec.paths[path]
            method_lower = method.lower()
            if method_lower in path_item:
                operation = path_item[method_lower]
                # Create operation object with responses attribute
                return type("Operation", (), {"responses": operation.get("responses", {}), "_raw": operation})()
        return None
