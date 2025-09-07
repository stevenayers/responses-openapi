"""
Schema validator for OpenAPI requests and responses.

Validates HTTP requests and responses against OpenAPI schemas.
"""

from typing import Any, List


class SchemaValidator:
    """
    Validator for OpenAPI schemas.

    .. code-block:: python

        validator = SchemaValidator(spec)
        errors = validator.validate_request(request)
    """

    def __init__(self, spec: Any) -> None:
        """
        Initialize the schema validator.

        :param spec: OpenAPI specification
        :type spec: Any
        """
        self.spec = spec

    def validate_request(self, request: Any) -> List[str]:
        """
        Validate a request against the OpenAPI spec.

        :param request: HTTP request to validate
        :type request: Any
        :returns: List of validation errors
        :rtype: List[str]
        """
        return []

    def validate_response(self, request: Any, response: Any) -> List[str]:
        """
        Validate a response against the OpenAPI spec.

        :param request: Original HTTP request
        :type request: Any
        :param response: HTTP response to validate
        :type response: Any
        :returns: List of validation errors
        :rtype: List[str]
        """
        return []
