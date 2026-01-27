"""Configuration validation with fail-fast philosophy."""

from typing import Dict, Any
from loguru import logger


class ConfigValidator:
    """Validate configuration with strict fail-fast approach."""

    def validate_all(
        self, config: Dict[str, Any], profiles: Dict[str, Dict[str, Any]]
    ) -> None:
        """
        Validate all configuration with fail-fast on any error.

        Args:
            config: Main configuration
            profiles: All loaded profiles

        Raises:
            ValueError: On any validation failure
        """
        self._validate_config_structure(config)
        self._validate_profile_structure(profiles)
        logger.info("All configuration validation passed")

    def _validate_config_structure(self, config: Dict[str, Any]) -> None:
        """Validate main config structure."""
        if not config:
            raise ValueError("Configuration is empty")

        # Check required sections
        if "wrapper" not in config:
            raise ValueError("Missing 'wrapper' section in config.yaml")

        # Validate wrapper settings
        wrapper = config["wrapper"]
        if "timeout" in wrapper and not isinstance(wrapper["timeout"], (int, float)):
            raise ValueError(f"Invalid timeout value: {wrapper['timeout']}")
        if "max_retries" in wrapper and not isinstance(wrapper["max_retries"], int):
            raise ValueError(f"Invalid max_retries value: {wrapper['max_retries']}")

    def _validate_profile_structure(self, profiles: Dict[str, Dict[str, Any]]) -> None:
        """Validate profile structure and parameters."""
        if not profiles:
            raise ValueError("No profiles found")

        for profile_path, profile_data in profiles.items():
            # Check if profile has model_id (Replicate) or endpoint (legacy)
            if "model_id" in profile_data or "endpoint" in profile_data:
                # New single-model profile format
                self._validate_single_profile(profile_path, profile_data)
            else:
                # Missing required field
                raise ValueError(
                    f"Profile '{profile_path}' missing required field. "
                    f"Profiles must include 'model_id' field."
                )

    def _validate_single_profile(
        self, profile_path: str, profile_data: Dict[str, Any]
    ) -> None:
        """Validate a single profile structure."""
        # Check required fields - model_id for Replicate
        model_id = profile_data.get("model_id") or profile_data.get("endpoint")
        if not model_id:
            raise ValueError(
                f"Profile '{profile_path}' missing required 'model_id' field"
            )

        # Validate project name (optional string)
        if "project" in profile_data and not isinstance(profile_data["project"], str):
            raise ValueError(
                f"Profile '{profile_path}' has invalid 'project' field (must be string)"
            )

        # Validate paths section (optional, contains input/output)
        if "paths" in profile_data:
            paths = profile_data["paths"]
            if not isinstance(paths, dict):
                raise ValueError(
                    f"Profile '{profile_path}' has invalid 'paths' field (must be dict)"
                )

            if "input" in paths:
                if paths["input"] is not None and not isinstance(paths["input"], str):
                    raise ValueError(
                        f"Profile '{profile_path}' paths.input must be string or null"
                    )

            if "output" in paths:
                if paths["output"] is not None and not isinstance(paths["output"], str):
                    raise ValueError(
                        f"Profile '{profile_path}' paths.output must be string or null"
                    )

        # Validate parameters (all profiles are now considered active)
        params = profile_data.get("parameters", {})

        # Validate image size if present
        if "image_size" in params:
            size = params["image_size"]
            # Accept both dict format (width/height) and string format (e.g., "1024x1024", "auto")
            if isinstance(size, dict):
                if "width" not in size or "height" not in size:
                    raise ValueError(
                        f"Profile '{profile_path}' image_size missing width or height"
                    )
            elif not isinstance(size, str):
                raise ValueError(
                    f"Profile '{profile_path}' has invalid image_size format (must be dict or string)"
                )
