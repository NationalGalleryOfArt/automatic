"""
Automatic - Runtime OpenAPI to FastAPI. No code generation.

A Python framework that dynamically creates FastAPI routes from OpenAPI
specifications at runtime, eliminating code generation.
"""

from .app import create_app
from .parser import OpenAPIParser
from .router import RouteGenerator
from .request_processor import RequestProcessor
from .validator import ResponseValidator
from .response_transformer import ResponseTransformer
from .exceptions import (
    BusinessException,
    ValidationError,
    NotFoundError,
    ConflictError,
    UnauthorizedError,
    ForbiddenError,
)
from .auth import APIKeyAuth, BearerTokenAuth, create_api_key_auth, create_bearer_auth
from .scaffold import ScaffoldGenerator
from .base import BaseCrudImplementation, BaseImplementation

__version__ = "0.1.0"
__all__ = [
    "create_app",
    "OpenAPIParser",
    "RouteGenerator",
    "RequestProcessor",
    "ResponseValidator",
    "ResponseTransformer",
    "BusinessException",
    "ValidationError",
    "NotFoundError",
    "ConflictError",
    "UnauthorizedError",
    "ForbiddenError",
    "APIKeyAuth",
    "BearerTokenAuth",
    "create_api_key_auth",
    "create_bearer_auth",
    "ScaffoldGenerator",
    "BaseCrudImplementation",
    "BaseImplementation",
]
