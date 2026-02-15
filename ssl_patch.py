"""
SSL patch for Python on Windows
This module patches SSL certificate verification to fix issues on Windows systems
"""

import os
import ssl
import certifi
import urllib3
import warnings

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create unverified context and patch the default SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Set environment variables for certificate verification
os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["PYTHONHTTPSVERIFY"] = "0"

# Patch requests library if available
try:
    import requests
    from requests.packages.urllib3.util import ssl_

    # Create a patched session class
    original_request = requests.Session.request

    def patched_request(self, method, url, **kwargs):
        # Disable SSL verification for all requests
        kwargs["verify"] = False
        return original_request(self, method, url, **kwargs)

    # Apply the patch
    requests.Session.request = patched_request

    # Also patch the default session
    requests.api.request = lambda method, url, **kwargs: patched_request(
        requests.Session(), method, url, **kwargs
    )

    print("Requests library patched to disable SSL verification")
except ImportError:
    print("Requests library not found, skipping patch")

# Patch httpx library if available
try:
    import httpx
    from httpx._config import DEFAULT_TIMEOUT_CONFIG
    from httpx._transports.default import HTTPTransport

    # Save the original create_ssl_context method
    original_create_ssl_context = httpx._transports.default.create_ssl_context

    # Create a patched create_ssl_context function
    def patched_create_ssl_context(verify=True, cert=None, trust_env=True):
        context = original_create_ssl_context(
            verify=False, cert=cert, trust_env=trust_env
        )
        return context

    # Apply the patch to the create_ssl_context function
    httpx._transports.default.create_ssl_context = patched_create_ssl_context

    # Create a patched transport class that inherits correctly
    class PatchedTransport(HTTPTransport):
        def __init__(
            self,
            verify=True,  # We'll ignore this parameter
            cert=None,
            http1=True,
            http2=False,
            limits=None,
            trust_env=True,
            proxy=None,
            retries=0,
            timeout=DEFAULT_TIMEOUT_CONFIG,
            **kwargs,
        ):
            # Call the parent constructor with verify=False
            super().__init__(
                verify=False,  # Always use False regardless of what was passed
                cert=cert,
                http1=http1,
                http2=http2,
                limits=limits,
                trust_env=trust_env,
                proxy=proxy,
                retries=retries,
                timeout=timeout,
                **kwargs,
            )

    # Apply the patch to HTTPX
    httpx.HTTPTransport = PatchedTransport

    # Also patch the Client class to always use verify=False
    original_client_init = httpx.Client.__init__

    def patched_client_init(self, *args, **kwargs):
        kwargs["verify"] = False
        original_client_init(self, *args, **kwargs)

    httpx.Client.__init__ = patched_client_init

    # Patch AsyncClient as well
    if hasattr(httpx, "AsyncClient"):
        original_async_client_init = httpx.AsyncClient.__init__

        def patched_async_client_init(self, *args, **kwargs):
            kwargs["verify"] = False
            original_async_client_init(self, *args, **kwargs)

        httpx.AsyncClient.__init__ = patched_async_client_init

    print("HTTPX library patched to disable SSL verification")
except ImportError:
    print("HTTPX library not found, skipping patch")
except Exception as e:
    print(f"Error patching HTTPX: {e}")
    warnings.warn(f"Could not fully patch HTTPX: {e}")

# Patch OpenAI client if available
try:
    import openai

    # Ensure the OpenAI client uses our patched httpx
    if hasattr(openai, "_client"):
        openai._client.httpx = httpx

    print("OpenAI client patched to disable SSL verification")
except ImportError:
    print("OpenAI client not found, skipping patch")
except Exception as e:
    print(f"Error patching OpenAI client: {e}")

# Patch DuckDuckGo search library if available
try:
    import duckduckgo_search
    from duckduckgo_search import DDGS
    import primp

    # Patch the primp library used by duckduckgo_search
    if hasattr(primp, "Client"):
        original_primp_init = primp.Client.__init__

        def patched_primp_init(self, *args, **kwargs):
            kwargs["verify"] = False
            original_primp_init(self, *args, **kwargs)

        primp.Client.__init__ = patched_primp_init

    # Also patch the DDGS class
    if hasattr(duckduckgo_search, "DDGS"):
        original_ddgs_init = DDGS.__init__

        def patched_ddgs_init(self, *args, **kwargs):
            # Don't add verify_ssl parameter as it's not supported
            # Just call the original init
            original_ddgs_init(self, *args, **kwargs)

        DDGS.__init__ = patched_ddgs_init

    print("DuckDuckGo search library patched to disable SSL verification")
except ImportError:
    print("DuckDuckGo search library not found, skipping patch")
except Exception as e:
    print(f"Error patching DuckDuckGo search library: {e}")

print(f"SSL certificate verification disabled")
print(f"Using certificate file: {certifi.where()}")
