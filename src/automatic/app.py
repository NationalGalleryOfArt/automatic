"""Main application interface for automatic framework."""

from typing import Optional, Union, Any
import importlib.util
from pathlib import Path
from fastapi import FastAPI
from datetime import datetime, timezone
from .parser import OpenAPIParser
from .router import RouteGenerator


def _add_health_check_endpoint(app: FastAPI):
    """Add a health check endpoint to the FastAPI app."""

    @app.get(
        "/health",
        summary="Health Check",
        description="Simple health check endpoint",
        tags=["Health"],
    )
    async def health_check():
        """
        Simple health check that returns basic service status.

        Returns service uptime and status without checking data sources.
        """
        return {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": "automatic",
        }


def create_app(
    spec_path: Optional[Union[str, Path]] = None,
    implementation: Optional[Any] = None,
    api_dir: Union[str, Path] = "specifications",
    impl_dir: Union[str, Path] = "implementations",
    auth_dependency: Optional[Any] = None,
    **kwargs,
) -> FastAPI:
    """
    Create a FastAPI application from OpenAPI specifications and implementations.

    Args:
        api_dir: Directory containing *.yaml spec files (default: "api")
        impl_dir: Directory containing implementation *.py files (default: "implementations")
        auth_dependency: Optional authentication dependency for all routes
        **kwargs: Additional arguments to pass to FastAPI constructor

    Returns:
        Configured FastAPI application

    Examples:
        >>> app = create_app()

        >>> from automatic.auth import create_api_key_auth
        >>> auth = create_api_key_auth(api_keys=['secret-key'])
        >>> app = create_app(auth_dependency=auth)
    """

    # Direct mode if spec_path and implementation are provided
    if spec_path and implementation:
        return _create_direct_app(spec_path, implementation, auth_dependency, **kwargs)

    # Automatic discovery mode
    return _create_automatic_app(api_dir, impl_dir, auth_dependency, **kwargs)


def _create_direct_app(
    spec_path: Union[str, Path],
    implementation: Any,
    auth_dependency: Optional[Any] = None,
    **kwargs,
) -> FastAPI:
    """Create app using direct spec and implementation."""
    # Create FastAPI app
    app_kwargs = {
        "title": "Automatic API",
        "description": "Direct API from automatic framework",
        "version": "1.0.0",
    }
    app_kwargs.update(kwargs)

    app = FastAPI(**app_kwargs)

    # Parse OpenAPI spec
    parser = OpenAPIParser(spec_path)
    parser.load_spec()

    # Generate routes with auth
    route_generator = RouteGenerator(implementation, auth_dependency=auth_dependency)
    routes = route_generator.generate_routes(parser)

    for route in routes:
        app.router.routes.append(route)

    # Add health check endpoint
    _add_health_check_endpoint(app)

    return app


def _create_automatic_app(
    api_dir: Union[str, Path],
    impl_dir: Union[str, Path],
    auth_dependency: Optional[Any] = None,
    **kwargs,
) -> FastAPI:
    """Create app using automatic file discovery."""
    api_path = Path(api_dir)
    impl_path = Path(impl_dir)

    # Create FastAPI app
    app_kwargs = {
        "title": "Automatic API",
        "description": "Automatic API from automatic framework",
        "version": "1.0.0",
    }
    app_kwargs.update(kwargs)

    app = FastAPI(**app_kwargs)

    # Discover spec/implementation pairs
    spec_impl_pairs = _discover_spec_impl_pairs(api_path, impl_path)

    if not spec_impl_pairs:
        raise ValueError(
            f"No matching spec/implementation pairs found in {api_path} and {impl_path}"
        )

    # Process each pair
    for spec_file, impl_file, prefix in spec_impl_pairs:
        # Load implementation
        implementation = _load_implementation(impl_file)

        # Parse OpenAPI spec
        parser = OpenAPIParser(spec_file)
        parser.load_spec()

        # Generate routes with prefix and auth
        route_generator = RouteGenerator(
            implementation, path_prefix=prefix, auth_dependency=auth_dependency
        )
        routes = route_generator.generate_routes(parser)

        for route in routes:
            app.router.routes.append(route)

    # Add health check endpoint
    _add_health_check_endpoint(app)

    return app


def _discover_spec_impl_pairs(api_dir: Path, impl_dir: Path):
    """Discover matching spec and implementation file pairs."""
    if not api_dir.exists():
        raise FileNotFoundError(f"API directory not found: {api_dir}")

    if not impl_dir.exists():
        raise FileNotFoundError(f"Implementation directory not found: {impl_dir}")

    pairs = []

    # Find all YAML files in api directory
    yaml_files = list(api_dir.glob("*.yaml")) + list(api_dir.glob("*.yml"))

    for yaml_file in yaml_files:
        # Get base name (without extension)
        base_name = yaml_file.stem

        # Look for matching Python file
        py_file = impl_dir / f"{base_name}.py"

        if py_file.exists():
            # Use base name as path prefix (e.g., users.yaml -> /users)
            prefix = f"/{base_name}"
            pairs.append((yaml_file, py_file, prefix))

    return pairs


def _load_implementation(impl_file: Path):
    """Load Implementation class from a Python file."""
    spec = importlib.util.spec_from_file_location("implementation_module", impl_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load implementation from {impl_file}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Look for standard Implementation class
    if not hasattr(module, "Implementation"):
        raise AttributeError(f"No 'Implementation' class found in {impl_file}")

    implementation_class = getattr(module, "Implementation")
    return implementation_class()
