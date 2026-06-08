"""1Password session management."""
import atexit
import os
import subprocess
import sys
import shutil
from loguru import logger
from ..exceptions import AuthenticationError


OP_CLI = shutil.which("op")


def ensure_op_cli() -> None:
    """Verify 1Password CLI is installed, fail fast if not."""
    if not OP_CLI:
        error_msg = (
            "1Password CLI not found. Please install it:\n"
            "  macOS: brew install --cask 1password-cli\n"
            "  Linux: See https://1password.com/downloads/command-line/\n"
            "  Windows: See https://1password.com/downloads/command-line/"
        )
        logger.error(error_msg)
        raise AuthenticationError(error_msg)


def ensure_op_auth() -> None:
    """Ensure 1Password CLI is authenticated, prompting if needed."""
    ensure_op_cli()

    try:
        subprocess.run(
            [OP_CLI, "account", "get"],
            check=True,
            capture_output=True,
            timeout=5
        )
        logger.debug("1Password session is active")
        return
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        logger.info("🔐 1Password authentication required...")

        try:
            signin_process = subprocess.Popen(
                [OP_CLI, "signin"],
                stdout=subprocess.PIPE,
                stderr=sys.stderr,
                stdin=sys.stdin,
                text=True
            )
            stdout, _ = signin_process.communicate(timeout=60)

            if signin_process.returncode != 0:
                error_msg = "Failed to authenticate with 1Password"
                logger.error(error_msg)
                raise AuthenticationError(error_msg)

            if stdout:
                for line in stdout.strip().split("\n"):
                    if line.startswith("export "):
                        line = line.replace("export ", "")
                        key, value = line.split("=", 1)
                        value = value.strip('"')
                        os.environ[key] = value
                        logger.debug(f"Set session variable: {key}")

            logger.success("✅ 1Password authentication successful")
        except subprocess.TimeoutExpired:
            error_msg = "Authentication timed out"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)
        except Exception as e:
            error_msg = f"Authentication failed: {e}"
            logger.error(error_msg)
            raise AuthenticationError(error_msg) from e


def cleanup_session() -> None:
    """Clear 1Password session tokens from environment."""
    env_vars = list(os.environ.keys())
    for key in env_vars:
        if key.startswith("OP_SESSION_"):
            del os.environ[key]
            logger.debug(f"Cleared session variable: {key}")


# Register cleanup on exit
atexit.register(cleanup_session)