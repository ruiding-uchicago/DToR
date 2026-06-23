"""Phoenix tracing setup for LangGraph observability.

This module provides setup and configuration for Arize Phoenix tracing
integration with LangGraph applications. Phoenix provides observability
and debugging capabilities for LLM applications.

References
----------
- https://arize.com/docs/phoenix/integrations/python/langgraph/langgraph-tracing
- https://github.com/Arize-ai/phoenix
"""

import os
from typing import Optional

# Try importing Phoenix - make it optional
try:
    from phoenix.otel import register as register_phoenix
    PHOENIX_AVAILABLE = True
except ImportError:
    PHOENIX_AVAILABLE = False
    register_phoenix = None


def setup_phoenix(
    project_name: Optional[str] = None,
    phoenix_host: Optional[str] = None,
    phoenix_port: Optional[int] = None,
    auto_instrument: bool = True
) -> Optional[object]:
    """Initialize and configure Arize Phoenix for tracing.

    Sets up Phoenix OpenTelemetry instrumentation for LangGraph applications.
    This enables automatic tracing of all LangGraph node executions, LLM calls,
    and other LangChain operations.

    Parameters
    ----------
    project_name : str, optional
        Name of the project in Phoenix. Defaults to environment variable
        PHOENIX_PROJECT_NAME or 'deep-research'.
    phoenix_host : str, optional
        Phoenix server host. Defaults to environment variable PHOENIX_HOST or 'localhost'.
    phoenix_port : int, optional
        Phoenix server port. Defaults to environment variable PHOENIX_PORT or 6006.
    auto_instrument : bool, default=True
        Whether to automatically instrument installed OpenInference dependencies.
        Should be True for LangGraph integration.

    Returns
    -------
    object | None
        The tracer provider if Phoenix is available and setup succeeds,
        None otherwise.

    Notes
    -----
    - Requires `arize-phoenix` and `openinference-instrumentation-langchain` packages.
    - Phoenix server must be running before starting the application.
    - To start Phoenix server: `phoenix serve`
    - The endpoint is explicitly set to the OpenTelemetry collector endpoint at
      http://{host}:{port}/v1/traces
    - All traces are automatically sent to the Phoenix server.
    - If Phoenix is not installed, this function returns None gracefully.

    Examples
    --------
    >>> tracer_provider = setup_phoenix(project_name="my-research-app")
    >>> if tracer_provider:
    ...     print("Phoenix tracing enabled")
    """
    if not PHOENIX_AVAILABLE:
        return None

    # Get configuration from environment or use defaults
    project = project_name or os.getenv("PHOENIX_PROJECT_NAME", "deep-research")
    host = phoenix_host or os.getenv("PHOENIX_HOST", "localhost")
    port = phoenix_port or int(os.getenv("PHOENIX_PORT", "6006"))

    # Construct the OpenTelemetry collector endpoint
    endpoint = f"http://{host}:{port}/v1/traces"

    # Allow override via environment variable
    endpoint = os.getenv("PHOENIX_ENDPOINT", endpoint)

    try:
        # Register Phoenix with explicit endpoint for OpenTelemetry collector
        tracer_provider = register_phoenix(
            project_name=project,
            endpoint=endpoint,
            auto_instrument=auto_instrument
        )
        print(f"✅ Phoenix tracing enabled. Endpoint: {endpoint}")
        return tracer_provider
    except Exception as e:
        # Log error but don't fail if Phoenix setup fails
        print(f"Warning: Phoenix setup failed: {e}")
        print("Continuing without Phoenix tracing...")
        return None


def get_phoenix_url(phoenix_host: Optional[str] = None, phoenix_port: Optional[int] = None) -> Optional[str]:
    """Get the Phoenix UI URL for trace viewing.

    Constructs the URL to the Phoenix web interface where traces can be viewed.

    Parameters
    ----------
    phoenix_host : str, optional
        Phoenix server host. Defaults to environment variable PHOENIX_HOST or 'localhost'.
    phoenix_port : int, optional
        Phoenix server port. Defaults to environment variable PHOENIX_PORT or 6006.

    Returns
    -------
    str | None
        The Phoenix UI URL, or None if Phoenix is not configured.
    """
    if not PHOENIX_AVAILABLE:
        return None

    host = phoenix_host or os.getenv("PHOENIX_HOST", "localhost")
    port = phoenix_port or int(os.getenv("PHOENIX_PORT", "6006"))
    return f"http://{host}:{port}"


def is_phoenix_enabled() -> bool:
    """Check if Phoenix tracing is available and enabled.

    Returns
    -------
    bool
        True if Phoenix is installed and available, False otherwise.
    """
    return PHOENIX_AVAILABLE

