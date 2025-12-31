"""1Password CLI authentication module - imports from split modules.

This module re-exports functions from auth.py and session_manager.py
to maintain backward compatibility.
"""

from .auth import get_api_key, load_auth_config
from .session_manager import ensure_op_cli, ensure_op_auth, cleanup_session

# Re-export all functions for backward compatibility
__all__ = ['get_api_key', 'load_auth_config', 'ensure_op_cli', 'ensure_op_auth', 'cleanup_session']