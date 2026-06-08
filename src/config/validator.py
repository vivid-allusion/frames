"""Configuration validation with fail-fast philosophy."""

from typing import Dict, Any, Callable, List
from loguru import logger


class ConfigValidator:
    """Validate configuration with strict fail-fast approach."""

    PARAMETER_VALIDATION_RULES: Dict[str, Callable[[str, Any], List[str]]] = {
        "image_size": lambda path, v: (
            ["image_size must be dict with width/height or string"]
            if isinstance(v, dict) and ("width" not in v or "height" not in v)
            else (["image_size must be dict or string"] if not isinstance(v, (dict, str)) else [])
        ),
    }

    def validate_all(
        self, config: Dict[str, Any], profiles: Dict[str, Dict[str, Any]]
    ) -> None:
        self._validate_config_structure(config)
        self._validate_profile_structure(profiles)
        logger.info("All configuration validation passed")

    def _validate_config_structure(self, config: Dict[str, Any]) -> None:
        if not config:
            raise ValueError("Configuration is empty")
        if "wrapper" not in config:
            raise ValueError("Missing 'wrapper' section in config.yaml")
        wrapper = config["wrapper"]
        if not isinstance(wrapper.get("timeout"), (int, float, type(None))):
            raise ValueError(f"Invalid timeout value: {wrapper['timeout']}")
        if not isinstance(wrapper.get("max_retries"), (int, type(None))):
            raise ValueError(f"Invalid max_retries value: {wrapper['max_retries']}")

    def _validate_profile_structure(self, profiles: Dict[str, Dict[str, Any]]) -> None:
        if not profiles:
            raise ValueError("No profiles found")
        for profile_path, profile_data in profiles.items():
            if "model_id" in profile_data or "endpoint" in profile_data:
                self._validate_single_profile(profile_path, profile_data)
            else:
                raise ValueError(
                    f"Profile '{profile_path}' missing required field. "
                    "Profiles must include 'model_id' field."
                )

    def _validate_single_profile(
        self, profile_path: str, profile_data: Dict[str, Any]
    ) -> None:
        model_id = profile_data.get("model_id") or profile_data.get("endpoint")
        if not model_id:
            raise ValueError(
                f"Profile '{profile_path}' missing required 'model_id' field"
            )

        self._validate_string_field(profile_data, "project", profile_path)
        self._validate_paths_section(profile_data, profile_path)
        self._validate_parameters(profile_data.get("parameters", {}), profile_path)

    def _validate_string_field(self, data: dict, field: str, profile_path: str) -> None:
        if field in data and not isinstance(data[field], str):
            raise ValueError(
                f"Profile '{profile_path}' has invalid '{field}' field (must be string)"
            )

    def _validate_paths_section(self, profile_data: dict, profile_path: str) -> None:
        if "paths" not in profile_data:
            return
        paths = profile_data["paths"]
        if not isinstance(paths, dict):
            raise ValueError(
                f"Profile '{profile_path}' has invalid 'paths' field (must be dict)"
            )
        for key in ("input", "output"):
            if key in paths and paths[key] is not None and not isinstance(paths[key], str):
                raise ValueError(
                    f"Profile '{profile_path}' paths.{key} must be string or null"
                )

    def _validate_parameters(self, params: dict, profile_path: str) -> None:
        for param_name, rule in self.PARAMETER_VALIDATION_RULES.items():
            if param_name in params:
                errors = rule(profile_path, params[param_name])
                if errors:
                    raise ValueError(
                        f"Profile '{profile_path}': {'; '.join(errors)}"
                    )
