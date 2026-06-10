"""Authentication module — 4-tier env var hierarchy.

Priority:
    1. Already-set env var (injected by OpenReel TUI or cloud wrapper)
    2. pass show openreel/<key> (GPG-encrypted, optional)
    3. .env file in project root (standalone mode)
    4. Hard exit if no key found
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional
from loguru import logger
from dotenv import load_dotenv
from ..exceptions import AuthenticationError

REQUIRED_KEY = "REPLICATE_API_TOKEN"


def _try_pass(key_name: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["pass", "show", f"openreel/{key_name}"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            logger.info("Retrieved {} from pass", key_name)
            return result.stdout.strip()
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        pass
    return None


def get_api_key() -> str:
    api_token = os.getenv(REQUIRED_KEY)
    if api_token:
        logger.info("Using {} from environment", REQUIRED_KEY)
        return api_token

    api_token = _try_pass(REQUIRED_KEY.lower())
    if api_token:
        os.environ[REQUIRED_KEY] = api_token
        return api_token

    from .env import get_replicate_api_token_from_env
    api_token = get_replicate_api_token_from_env()
    if api_token:
        return api_token

    raise AuthenticationError(
        "REPLICATE_API_TOKEN not set.\n"
        "  - Set as env var  (export REPLICATE_API_TOKEN=...)\n"
        "  - Store in pass   (pass insert openreel/replicate_api_token)\n"
        "  - Add to .env     (echo REPLICATE_API_TOKEN=... > .env)"
    )


__all__ = ["get_api_key"]
