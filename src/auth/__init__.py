"""Authentication module for API access - prioritizes .env over 1Password."""
from typing import Optional
from .env import get_replicate_api_token_from_env
from .onepassword import get_api_key as get_api_key_from_op, ensure_op_auth

__all__ = ["get_api_key", "ensure_op_auth", "cleanup_session"]


def get_api_key() -> str:
    """
    Retrieve API key with .env priority over 1Password.
    
    Priority:
    1. REPLICATE_API_TOKEN from .env file or environment
    2. 1Password CLI fallback
    
    Returns:
        API token string
        
    Raises:
        ValueError: If no API token can be found
    """
    api_token = get_replicate_api_token_from_env()
    if api_token:
        return api_token
    
    return get_api_key_from_op()


def cleanup_session() -> None:
    """Clean up 1Password session if needed."""
    try:
        import subprocess
        subprocess.run(["op", "signout"], capture_output=True)
    except Exception:
        pass