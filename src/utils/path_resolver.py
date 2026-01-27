"""Path resolution utilities with USER-FILES fallback."""

from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from loguru import logger


USER_FILES_INPUT = Path("USER-FILES/04.INPUT")
USER_FILES_OUTPUT = Path("USER-FILES/05.OUTPUT")


def resolve_input_path(
    config: Dict[str, Any], profiles: list[Dict[str, Any]], profiles_dir: Path
) -> Tuple[Path, Optional[str]]:
    """
    Resolve input path from config, profiles, or USER-FILES fallback.

    Args:
        config: Main configuration dict
        profiles: List of active profile dicts
        profiles_dir: Directory containing profiles

    Returns:
        Tuple of (resolved input Path, project name or None)

    Raises:
        FileNotFoundError: If resolved path doesn't exist
    """
    custom_input_path = None
    project_name = None

    for profile in profiles:
        if profile.get("paths", {}).get("input"):
            custom_input_path = profile["paths"]["input"]
            project_name = profile.get("project", "")
            break

    if custom_input_path:
        input_path = Path(custom_input_path)
        logger.info(f"Using custom input path: {input_path}")
    else:
        input_path = Path(config["inputs"]["directory"])
        logger.info(f"Using default input path: {input_path}")

    if not input_path.exists():
        raise FileNotFoundError(f"Input directory not found: {input_path}")

    return input_path, project_name


def resolve_output_base_path(
    config: Dict[str, Any], profiles: list[Dict[str, Any]]
) -> Path:
    """
    Resolve output base path from config, profiles, or USER-FILES fallback.

    Args:
        config: Main configuration dict
        profiles: List of active profile dicts

    Returns:
        Resolved output base Path
    """
    custom_output_path = None

    for profile in profiles:
        if profile.get("paths", {}).get("output"):
            custom_output_path = profile["paths"]["output"]
            break

    if custom_output_path:
        output_base = Path(custom_output_path)
        logger.info(f"Using custom output path: {output_base}")
    else:
        output_base = Path(config["outputs"]["directory"])
        logger.info(f"Using default output path: {output_base}")

    return output_base


def create_timestamped_output_path(base_path: Path) -> Path:
    """
    Create timestamped subdirectory inside base path.

    Args:
        base_path: Base output directory

    Returns:
        Path to new timestamped directory
    """
    from datetime import datetime
    from src.constants import TIMESTAMP_FORMAT

    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    output_path = base_path / f"{timestamp}_IMAGE"
    output_path.mkdir(parents=True, exist_ok=True)

    return output_path


def validate_single_custom_input_path(profiles: list[Dict[str, Any]]) -> None:
    """
    Ensure only one profile has a custom input path.

    Args:
        profiles: List of active profile dicts

    Raises:
        ValueError: If multiple profiles have custom input paths
    """
    custom_paths = [
        p["paths"]["input"] for p in profiles if p.get("paths", {}).get("input")
    ]

    if len(custom_paths) > 1:
        raise ValueError(
            f"Multiple profiles have custom input paths: {custom_paths}. "
            "Only one custom input path is allowed."
        )


def validate_path_exists(path: Path, path_type: str) -> None:
    """
    Validate path exists with fail-fast behavior.

    Args:
        path: Path to validate
        path_type: Descriptive name for error messages

    Raises:
        FileNotFoundError: If path doesn't exist
    """
    if not path.exists():
        raise FileNotFoundError(f"{path_type} directory not found: {path}")
