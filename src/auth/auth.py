"""Authentication module for Replicate API access."""
import subprocess
import shutil
from pathlib import Path
import yaml
from loguru import logger
from ..exceptions import AuthenticationError, ConfigurationError
from .session_manager import ensure_op_cli, ensure_op_auth


OP_CLI = shutil.which("op")


def load_auth_config() -> dict:
    """Load 1Password configuration from any auth*.yaml file."""
    config_dir = Path(__file__).parent.parent.parent / "USER-FILES" / "01.CONFIG"
    
    # Find all files starting with "auth" and ending with .yaml or .yml
    auth_files = list(config_dir.glob("auth*.yaml")) + list(config_dir.glob("auth*.yml"))
    
    if not auth_files:
        error_msg = f"No auth configuration found in {config_dir} (looking for auth*.yaml or auth*.yml)"
        logger.error(error_msg)
        raise ConfigurationError(error_msg)
    
    # Use the first auth file found (sorted alphabetically)
    config_path = sorted(auth_files)[0]
    logger.debug(f"Using auth config: {config_path.name}")

    try:
        with open(config_path) as f:
            config = yaml.safe_load(f)

        if not config or "onepassword" not in config:
            error_msg = f"Invalid {config_path.name}: missing 'onepassword' section"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

        op_config = config["onepassword"]
        if "item" not in op_config or "field" not in op_config:
            error_msg = f"Invalid {config_path.name}: 'onepassword' must have 'item' and 'field'"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)

        return op_config
    except Exception as e:
        error_msg = f"Failed to load auth configuration: {e}"
        logger.error(error_msg)
        raise ConfigurationError(error_msg) from e


def get_api_key() -> str:
    """Retrieve Replicate API key from 1Password."""
    ensure_op_cli()
    ensure_op_auth()

    config = load_auth_config()
    item_name = config["item"]
    field_name = config["field"]

    try:
        result = subprocess.run(
            [OP_CLI, "item", "get", item_name, "--field", field_name],
            check=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        api_key = result.stdout.strip()
        if not api_key:
            error_msg = "Empty API key retrieved from 1Password"
            logger.error(error_msg)
            raise AuthenticationError(error_msg)

        masked_key = f"{api_key[:4]}..." if len(api_key) > 4 else "***"
        logger.debug(f"Retrieved API key: {masked_key}")

        # Delete .env file if authentication successful
        env_file = Path(__file__).parent.parent.parent / ".env"
        if env_file.exists():
            try:
                env_file.unlink()
                logger.info("Removed deprecated .env file")
            except Exception as e:
                logger.warning(f"Could not remove .env file: {e}")

        return api_key
    except subprocess.CalledProcessError as e:
        error_msg = (
            f"Failed to retrieve API key from 1Password:\n"
            f"  Item: {item_name}\n"
            f"  Field: {field_name}\n"
            f"  Error: {e.stderr if e.stderr else 'Unknown error'}"
        )
        logger.error(error_msg)
        raise AuthenticationError(error_msg) from e
    except subprocess.TimeoutExpired:
        error_msg = "Timed out retrieving API key"
        logger.error(error_msg)
        raise AuthenticationError(error_msg)