# automatic

**Zero Configuration OpenAPI Framework**

A Python framework that automatically creates FastAPI routes from OpenAPI specifications with **Rails-style base classes**, **intelligent auto-discovery**, and **built-in authentication**.

## Key Features

### 🚀 Zero Configuration Auto-Discovery
- **Ultimate simplicity**: Just run `automatic` to set up complete projects
- **Smart detection**: Automatically detects first-run vs incremental mode
- **Multi-spec support**: Processes all OpenAPI specs in one command

### 🏗️ Rails-Style Base Classes
- **BaseCrudImplementation**: Automatic CRUD operation delegation for REST APIs
- **BaseImplementation**: Helper methods for custom business logic
- **Intelligent selection**: Auto-detects CRUD vs custom patterns

### 🔐 Built-in Authentication
- **API Key & Bearer Token**: Built-in authentication with metadata support
- **Flexible configuration**: Lists, dicts, environment variables
- **Auth context**: Authentication info passed to all methods

### 🛡️ Comprehensive Error Handling
- **Business exceptions**: NotFoundError, ValidationError, ConflictError, etc.
- **RFC 9457 compliance**: Standardized error response format
- **Automatic mapping**: Business exceptions → HTTP status codes

### 🏥 Built-in Health Monitoring
- **Automatic `/health` endpoint**: Added to every application
- **Service identification**: For monitoring and health checks

## How It Works

Just run `automatic` in any directory with OpenAPI specs - that's it!

```bash
# Place your OpenAPI specs anywhere
ls *.yaml
# users.yaml  orders.yaml  products.yaml

# One command setup
automatic
# ✅ Complete project structure created
# ✅ All implementations generated with proper base classes  
# ✅ main.py configured and ready to run

python main.py  # Your API is live!
```

## Quick Start

### 1. Ultimate Simplicity - Zero Configuration
```bash
# Just run automatic in any directory with OpenAPI specs
automatic

# Creates this structure automatically:
# ├── specifications/
# │   ├── users.yaml         # Your specs moved here
# │   └── orders.yaml        
# ├── implementations/
# │   ├── user_service.py    # Generated with CRUD base class
# │   └── order_service.py   # Generated with custom base class  
# ├── main.py                # Auto-generated FastAPI app
# └── .gitignore             # Python gitignore
```

### 2. Generated CRUD Implementation (Rails-style)
```python
# implementations/user_service.py - Auto-generated!
from automatic import BaseCrudImplementation

class UserService(BaseCrudImplementation):
    resource_name = "user"

    def get_data_store(self):
        return self._data_store  # Replace with your database

    def index(self, filters=None, auth_info=None):
        # List users (business logic only)
        return super().index(filters, auth_info)

    def show(self, resource_id, auth_info=None):
        # Show a user (business logic only)
        return super().show(resource_id, auth_info)

    def create(self, data, auth_info=None):
        # Create a user (business logic only)
        return super().create(data, auth_info)

    def update(self, resource_id, data, auth_info=None):
        # Update a user (business logic only)
        return super().update(resource_id, data, auth_info)

    def destroy(self, resource_id, auth_info=None):
        # Delete a user (business logic only)
        return super().destroy(resource_id, auth_info)
```
### 2. Generated CRUD Implementation (Rails-style)

**Note:** The router now handles all HTTP parameter extraction and error mapping. The generated CRUD implementation contains only business logic methods with explicit arguments, making your code minimal and easy to test.
```python
# implementations/user_service.py - Auto-generated!
from automatic import BaseCrudImplementation

class UserService(BaseCrudImplementation):
    resource_name = "user"
    
    def get_data_store(self):
        return self._data_store  # Replace with your database
    
    def get_user(self, data):
        # Automatically delegates to self.show()
        return self.show(data.get('user_id'), auth_info=data.get('auth'))
    
    def create_user(self, data):
        # Automatically delegates to self.create()  
        return self.create(data=data.get('body', {}), auth_info=data.get('auth'))
```

### 3. Custom Business Logic
```python
# implementations/report_service.py - For non-CRUD APIs
from automatic import BaseImplementation

class ReportService(BaseImplementation):
    def generate_report(self, data):
        # Use built-in get_data() for external services
        external_data = await self.get_data("analytics", "daily", data.get('auth'))
        # Status code automatically inferred (POST=201)
        return {"report_id": "123", "status": "generated"}
```

### 4. Built-in Authentication
```python
# main.py - Auto-generated with auth support
from automatic import create_app, create_api_key_auth

auth = create_api_key_auth(api_keys=['secret-key-123'])
app = create_app(auth_dependency=auth)

# Now all endpoints require X-API-Key header
```

**Your API is ready!** Visit http://localhost:8000/docs for interactive documentation.

## Current Feature Set

**automatic** includes the following features:

### ✅ Request & Response Validation
- Automatic validation against OpenAPI schema
- Path, query, and body parameter extraction
- Type coercion and format validation
- Pydantic model generation from OpenAPI specs
- **Automatic HTTP status code inference** from method types

### ✅ Advanced Error Handling  
- Standard RFC 9457 error response format
- Business exception to HTTP status code mapping
- Built-in exceptions: NotFoundError, ValidationError, ConflictError, etc.
- Custom error handling with context preservation

### ✅ Production Authentication
- API key authentication (X-API-Key header)
- Bearer token authentication (Authorization header)
- Flexible token storage (lists, dicts, env vars)
- Authentication context passed to all methods

### ✅ Enterprise Features
- Built-in `/health` endpoint for monitoring
- Multi-API project support with auto-discovery
- Version-aware routing (v1, v2, etc.)
- Comprehensive logging and error tracking

## Installation

```bash
# Install from source
git clone <repository-url>
cd automatic
pip install -e .
```

## Running Tests

The project uses pytest for testing. Run tests with:

```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test file
python -m pytest tests/test_basic.py -v

# Run with coverage (if you have pytest-cov installed)
python -m pytest tests/ --cov=src/automatic -v
```

## Usage Options

### Automatic Discovery (Default)
```python
# Zero config - uses ./api/ and ./implementations/
app = automatic.create_app()

# Custom directories
app = automatic.create_app(api_dir="specs", impl_dir="handlers")
```

## Implementation Interface

### CRUD APIs

For CRUD APIs, the generated implementation contains only the standard CRUD methods with explicit arguments. The router handles all HTTP parameter extraction and calls these methods directly:

```python
class UserService(BaseCrudImplementation):
    def index(self, filters=None, auth_info=None):
        # List users (business logic only)
        return super().index(filters, auth_info)

    def show(self, resource_id, auth_info=None):
        # Show a user (business logic only)
        return super().show(resource_id, auth_info)

    def create(self, data, auth_info=None):
        # Create a user (business logic only)
        return super().create(data, auth_info)

    def update(self, resource_id, data, auth_info=None):
        # Update a user (business logic only)
        return super().update(resource_id, data, auth_info)

    def destroy(self, resource_id, auth_info=None):
        # Delete a user (business logic only)
        return super().destroy(resource_id, auth_info)
```

### Non-CRUD APIs

For non-CRUD APIs, you can still define methods matching OpenAPI `operationId` values, which will receive a combined `data` dict as before:

```python
class Implementation:
    def my_operation(self, data: dict) -> dict:
        # Custom business logic for non-CRUD endpoints
        # Status code automatically inferred from HTTP method
        return {"result": "success"}
```

### Automatic Status Code Inference

For non-CRUD methods, HTTP status codes are automatically inferred from the HTTP method:
- **GET** → 200 (OK)
- **POST** → 201 (Created)
- **PUT** → 200 (OK)
- **PATCH** → 200 (OK)
- **DELETE** → 204 (No Content)

You can still return `(data, status_code)` tuples for custom status codes.

### Version-aware methods and error handling

You can still use version-aware methods and custom error handlers as described below for non-CRUD endpoints.

## Error Handling

Implementations can include an optional `handle_error` method to provide custom error handling:

```python
def handle_error(self, error: Exception) -> tuple[dict, int]:
    """Custom error handling logic"""
    if isinstance(error, ValueError):
        return {"error": str(error)}, 400
    elif isinstance(error, NotFoundError):
        return {"error": "Resource not found"}, 404
    return {"error": "Internal server error"}, 500
```

This allows for:
- Custom error response formatting
- HTTP status code mapping
- Error type-specific handling
- Consistent error responses across endpoints

## Shared Business Logic

Implementations can easily import and use each other:

```python
# implementations/orders.py
class Implementation:
    def create_order(self, data):
        # Import users service
        from .users import Implementation as UserService
        user_service = UserService()
        
        # Validate user exists
        user, status = user_service.get_user({"user_id": data["user_id"]})
        if status != 200:
            return {"error": "User not found"}, 400
            
        return {"order_id": 123, "user_id": data["user_id"]}, 201
```

## Working Example

A complete working example is available in the `examples/convention-demo/` directory:

```bash
# Run the automatic discovery demo
cd examples/convention-demo
python main.py
```

This demonstrates:
- **Zero-config setup**: Just `automatic.create_app()`
- **Multiple APIs**: Users and Orders with shared business logic
- **Path prefixing**: `users.yaml` → `/users/*` routes
- **Inter-service communication**: Orders service validates users

### Example API calls:

```bash
# Users API
curl http://localhost:8000/users
curl http://localhost:8000/users/1
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Charlie"}'

# Orders API (validates users exist)
curl http://localhost:8000/orders
curl -X POST http://localhost:8000/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "total": 75.00}'
```

Visit http://localhost:8000/docs for interactive API documentation.

## API Versioning

Automatic supports clean API versioning where a single method can handle multiple versions:

### Version Detection

The framework automatically extracts version information from:
- **Filenames**: `users_v2.yaml` → version 2
- **OperationIds**: `create_user_v2` → version 2  
- **Default**: version 1 if no version specified

### Version-Aware Implementation

```python
class Implementation:
    def get_user(self, data, version=1):
        user = self._get_user_data(data["user_id"])
        
        if version == 1:
            # Status code automatically inferred (GET=200)
            return {"user_id": user.id, "name": user.name}
        elif version == 2:
            return {
                "user_id": user.id,
                "full_name": user.full_name,
                "email": user.email
            }
        elif version == 3:
            return {
                "user_id": user.id,
                "profile": {
                    "full_name": user.full_name,
                    "email": user.email,
                    "preferences": user.preferences
                }
            }
        else:
            raise UnsupportedVersionError(f"Version {version} not supported")
```

### Versioning Example

A complete versioning example is available in `examples/versioning/`:

```bash
# Run the versioned API example
cd examples/versioning
python run_versioned_example.py
```

Test different versions:
```bash
# v1 API - simple format
curl -X POST "http://localhost:8000/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John", "email": "john@example.com"}'

# v2 API - enhanced format  
curl -X POST "http://localhost:8000/v2/users" \
  -H "Content-Type: application/json" \
  -d '{"full_name": "Jane Doe", "email": "jane@example.com"}'

# Same user, different response formats
curl "http://localhost:8000/v1/users/1"  # {"user_id": 1, "name": "John"}
curl "http://localhost:8000/v2/users/1"  # {"user_id": 1, "full_name": "John Doe", "email": "john@example.com"}
curl "http://localhost:8000/v3/users/1"  # {"user_id": 1, "profile": {...}}
```

### Benefits

- **DRY Principle**: Single method handles all versions
- **Easy Migration**: Gradual version transitions
- **Clean Deprecation**: Clear error messages for deprecated versions
- **Maintainable**: Version logic contained within implementation
- **Backward Compatible**: Existing methods without version parameters work unchanged
