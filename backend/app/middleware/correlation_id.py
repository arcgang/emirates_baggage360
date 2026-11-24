"""Correlation ID middleware for request tracing."""
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and propagate correlation IDs for request tracing.
    Implements FR-016 requirement for audit trail correlation.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Generate or extract correlation ID and attach to request state.
        
        The correlation ID is:
        1. Extracted from X-Correlation-ID header if present
        2. Generated as a new UUID if not present
        3. Attached to request.state for use in audit logging
        4. Returned in response X-Correlation-ID header
        """
        # Extract or generate correlation ID
        correlation_id = request.headers.get("X-Correlation-ID")
        if not correlation_id:
            correlation_id = str(uuid.uuid4())
        
        # Attach to request state for use in route handlers and services
        request.state.correlation_id = correlation_id
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        
        return response


def get_correlation_id(request: Request) -> str:
    """
    Helper function to retrieve correlation ID from request state.
    
    Args:
        request: Starlette Request object
    
    Returns:
        Correlation ID string
    """
    return getattr(request.state, "correlation_id", str(uuid.uuid4()))
