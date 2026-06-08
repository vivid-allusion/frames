"""Authentication module - 1Password CLI integration."""

from .onepassword import get_api_key, ensure_op_auth, ensure_op_cli, cleanup_session

__all__ = ["get_api_key", "ensure_op_auth", "ensure_op_cli", "cleanup_session"]
