"""
responses-openapi: OpenAPI-driven HTTP mocking for pytest.

Automatically generate mock responses from OpenAPI specifications.
"""

from .core import OpenAPIMocker

__version__ = "0.1.0"
__all__ = ["OpenAPIMocker"]
