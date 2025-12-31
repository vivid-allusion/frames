#!/usr/bin/env python
"""Test script for 1Password authentication integration."""

import sys
from pathlib import Path
from loguru import logger

sys.path.insert(0, str(Path(__file__).parent))

from src.auth.onepassword import ensure_op_cli, ensure_op_auth, get_api_key, cleanup_session


def main():
    """Test 1Password authentication flow."""
    logger.info("Testing 1Password CLI authentication...")

    try:
        logger.info("Step 1: Checking 1Password CLI installation...")
        ensure_op_cli()
        logger.success("✅ 1Password CLI found")

        logger.info("Step 2: Testing authentication...")
        ensure_op_auth()
        logger.success("✅ Authentication successful")

        logger.info("Step 3: Retrieving API key...")
        api_key = get_api_key()
        logger.success(f"✅ API key retrieved: {api_key[:8]}...")

        logger.info("Step 4: Cleaning up session...")
        cleanup_session()
        logger.success("✅ Session cleaned up")

        logger.success("\n🎉 All authentication tests passed!")
        return 0

    except SystemExit as e:
        logger.error(f"❌ Test failed with exit code: {e.code}")
        return e.code
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())