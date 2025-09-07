"""
Core OpenAPI mocker implementation.

Provides the main OpenAPIMocker class that orchestrates mocking
of HTTP responses based on OpenAPI specifications.
"""

import json
import random
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import responses
import yaml
from faker import Faker
from requests import PreparedRequest


class OpenAPIMocker:
    """
    Main class for mocking HTTP responses based on OpenAPI specifications.

    .. code-block:: python

        with OpenAPIMocker('petstore.yaml') as mocker:
            # Make requests that will be mocked
            response = requests.get('https://api.example.com/pets')
    """

    def __init__(self, spec_path: Optional[str] = None, **options: Any) -> None:
        """
        Initialize the OpenAPI mocker.

        :param spec_path: Path to OpenAPI specification file
        :type spec_path: Optional[str]
        :param options: Additional configuration options
        :type options: Any
        """
        self.spec_path = spec_path
        self.spec: Optional[Dict[str, Any]] = None
        self.options = options
        self.responses_mock = responses.RequestsMock(assert_all_requests_are_fired=False)
        self.faker = Faker(self.options.get("faker_locale", "en_US"))
        # Set seed for reproducible tests if provided
        if "faker_seed" in self.options:
            Faker.seed(self.options["faker_seed"])
            random.seed(self.options["faker_seed"])

        if spec_path:
            self.load_spec(spec_path)

    def load_spec(self, spec_path: str) -> None:
        """
        Load an OpenAPI specification from file.

        :param spec_path: Path to the specification file
        :type spec_path: str
        :raises FileNotFoundError: If spec file doesn't exist
        :raises ValueError: If spec format is unsupported
        """
        path = Path(spec_path)

        if not path.exists():
            raise FileNotFoundError(f"Spec file not found: {spec_path}")

        with path.open("r") as f:
            if path.suffix in [".yaml", ".yml"]:
                self.spec = yaml.safe_load(f)
            elif path.suffix == ".json":
                self.spec = json.load(f)
            else:
                raise ValueError(f"Unsupported spec format: {path.suffix}")

        self._register_routes()

    def _register_routes(self) -> None:
        """
        Register all routes from the OpenAPI spec with responses.
        """
        if not self.spec or "paths" not in self.spec:
            return

        base_url = self.options.get("base_url", "http://localhost")

        for path, path_item in self.spec["paths"].items():
            for method, operation in path_item.items():
                if method in ["get", "post", "put", "delete", "patch", "head", "options"]:
                    self._register_operation(method.upper(), path, operation, base_url)

    def _register_operation(self, method: str, path: str, operation: Dict[str, Any], base_url: str) -> None:
        """
        Register a single operation with responses.

        :param method: HTTP method
        :type method: str
        :param path: API path
        :type path: str
        :param operation: Operation specification
        :type operation: Dict[str, Any]
        :param base_url: Base URL for the API
        :type base_url: str
        """
        # Convert OpenAPI path to regex (simple conversion for minimal example)
        # {petId} -> (?P<petId>[^/]+)
        import re

        regex_path = re.sub(r"\{([^}]+)\}", r"(?P<\1>[^/]+)", path)
        full_url = f"{base_url.rstrip('/')}{regex_path}"

        def callback(request: PreparedRequest) -> Tuple[int, Dict[str, str], str]:
            # Generate a simple response based on the spec
            responses_spec = operation.get("responses", {})

            # Use 200 response if available, otherwise first response
            if "200" in responses_spec:
                response_spec = responses_spec["200"]
            else:
                response_spec = list(responses_spec.values())[0] if responses_spec else {}

            # Generate simple response
            response_body = {}

            # Try to use example if available
            content = response_spec.get("content", {})
            if "application/json" in content:
                json_content = content["application/json"]

                # Use example if provided
                if "example" in json_content:
                    response_body = json_content["example"]
                elif "schema" in json_content:
                    # Generate minimal response from schema
                    schema = json_content["schema"]
                    response_body = self._generate_from_schema(schema)

            return 200, {}, json.dumps(response_body)

        self.responses_mock.add_callback(method, re.compile(full_url), callback=callback)

    def _generate_from_schema(self, schema: Dict[str, Any]) -> Any:
        """
        Generate realistic data from a JSON schema using Faker.

        :param schema: JSON schema
        :type schema: Dict[str, Any]
        :returns: Generated data
        :rtype: Any
        """
        if "$ref" in schema:
            # Handle references (simplified for minimal example)
            ref_path = schema["$ref"].split("/")
            if ref_path[0] == "#" and len(ref_path) > 1:
                # Internal reference
                ref_schema = self.spec
                for part in ref_path[1:]:
                    ref_schema = ref_schema.get(part, {})
                return self._generate_from_schema(ref_schema)

        schema_type = schema.get("type", "object")

        if schema_type == "array":
            items_schema = schema.get("items", {})
            # Generate random number of items (1-3)
            min_items = schema.get("minItems", 1)
            max_items = schema.get("maxItems", 3)
            num_items = random.randint(min_items, min(max_items, 3))
            return [self._generate_from_schema(items_schema) for _ in range(num_items)]

        elif schema_type == "object":
            result = {}
            properties = schema.get("properties", {})
            required_fields = schema.get("required", [])

            for prop_name, prop_schema in properties.items():
                # Always include required fields, randomly include optional ones
                if prop_name in required_fields or random.random() > 0.3:
                    result[prop_name] = self._generate_from_schema(prop_schema)
            return result

        elif schema_type == "string":
            return self._generate_string(schema)

        elif schema_type == "integer":
            return self._generate_integer(schema)

        elif schema_type == "number":
            return self._generate_number(schema)

        elif schema_type == "boolean":
            return self.faker.boolean()

        return None

    def _generate_string(self, schema: Dict[str, Any]) -> str:
        """
        Generate a realistic string based on schema constraints.

        :param schema: String schema
        :type schema: Dict[str, Any]
        :returns: Generated string
        :rtype: str
        """
        # Handle enum
        if "enum" in schema:
            return random.choice(schema["enum"])

        # Handle format
        format_type = schema.get("format", "")

        if format_type == "email":
            return self.faker.email()
        elif format_type == "uuid":
            return str(self.faker.uuid4())
        elif format_type == "date":
            return self.faker.date()
        elif format_type == "date-time":
            return self.faker.iso8601()
        elif format_type == "uri" or format_type == "url":
            return self.faker.url()
        elif format_type == "ipv4":
            return self.faker.ipv4()
        elif format_type == "ipv6":
            return self.faker.ipv6()

        # Handle pattern (simplified - just use appropriate faker)
        pattern = schema.get("pattern", "")

        # Generate based on common property names
        # This is a heuristic approach for better mock data
        if "name" in pattern.lower() or "name" in str(schema.get("description", "")).lower():
            return self.faker.name()

        # Handle length constraints
        max_length = schema.get("maxLength", 50)

        # Generate a reasonable string
        if max_length <= 10:
            return self.faker.word()[:max_length]
        elif max_length <= 50:
            return self.faker.sentence(nb_words=3)[:max_length]
        else:
            return self.faker.text(max_nb_chars=min(max_length, 200))

    def _generate_integer(self, schema: Dict[str, Any]) -> int:
        """
        Generate a realistic integer based on schema constraints.

        :param schema: Integer schema
        :type schema: Dict[str, Any]
        :returns: Generated integer
        :rtype: int
        """
        # Handle enum
        if "enum" in schema:
            return random.choice(schema["enum"])

        # Get constraints
        minimum = schema.get("minimum", 0)
        maximum = schema.get("maximum", 10000)

        # Handle exclusive bounds
        if schema.get("exclusiveMinimum"):
            minimum += 1
        if schema.get("exclusiveMaximum"):
            maximum -= 1

        # Handle format hints
        format_type = schema.get("format", "")

        if format_type == "int64":
            # Generate larger numbers for int64
            if maximum == 10000 and minimum == 0:  # No explicit constraints
                return self.faker.random_int(min=1, max=999999)
        elif format_type == "int32":
            # Keep within int32 bounds
            maximum = min(maximum, 2147483647)
            minimum = max(minimum, -2147483648)

        return self.faker.random_int(min=minimum, max=maximum)

    def _generate_number(self, schema: Dict[str, Any]) -> float:
        """
        Generate a realistic number based on schema constraints.

        :param schema: Number schema
        :type schema: Dict[str, Any]
        :returns: Generated number
        :rtype: float
        """
        # Handle enum
        if "enum" in schema:
            return random.choice(schema["enum"])

        # Get constraints
        minimum = schema.get("minimum", 0.0)
        maximum = schema.get("maximum", 1000.0)

        # Handle exclusive bounds
        if schema.get("exclusiveMinimum"):
            minimum += 0.01
        if schema.get("exclusiveMaximum"):
            maximum -= 0.01

        # Generate and round to 2 decimal places
        return round(random.uniform(minimum, maximum), 2)

    def start(self) -> None:
        """
        Start mocking HTTP responses.
        """
        self.responses_mock.start()

    def stop(self) -> None:
        """
        Stop mocking HTTP responses.
        """
        try:
            self.responses_mock.stop()
        except TypeError:
            # Older versions of responses don't have this parameter
            self.responses_mock.stop()

    def cleanup(self) -> None:
        """
        Clean up resources and reset mocks.
        """
        self.responses_mock.reset()

    def __enter__(self) -> "OpenAPIMocker":
        """
        Context manager entry.

        :returns: Self
        :rtype: OpenAPIMocker
        """
        self.start()
        return self

    def __exit__(self, *args: Any) -> None:
        """
        Context manager exit.

        :param args: Exception information
        :type args: Any
        """
        self.stop()
        self.cleanup()
