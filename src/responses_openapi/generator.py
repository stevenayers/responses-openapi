"""
Response generator for OpenAPI schemas.

Generates mock responses based on OpenAPI response schemas.
"""

from typing import Any, Dict


class ResponseGenerator:
    """
    Generator for mock responses from OpenAPI schemas.

    .. code-block:: python

        generator = ResponseGenerator(spec)
        response = generator.generate_response(operation, 200)
    """

    def __init__(self, spec: Any, faker_locale: str = "en_US") -> None:
        """
        Initialize the response generator.

        :param spec: OpenAPI specification
        :type spec: Any
        :param faker_locale: Locale for Faker
        :type faker_locale: str
        """
        self.spec = spec
        self.faker_locale = faker_locale

    def generate_response(self, operation: Any, status_code: int = 200) -> Dict[str, Any]:
        """
        Generate a mock response for an operation.

        :param operation: OpenAPI operation
        :type operation: Any
        :param status_code: HTTP status code
        :type status_code: int
        :returns: Generated response data
        :rtype: Dict[str, Any]
        """
        return {"status": status_code, "json": {"message": "Mock response"}, "headers": {}}
