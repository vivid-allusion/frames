"""Configuration loading for Replicate wrapper."""

import sys
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger

from ..processing.discovery import InputDiscovery


class ConfigLoader:
    """Load and manage configuration files."""

    def __init__(self, config_dir: Path | None = None):
        """
        Initialize config loader.

        Args:
            config_dir: Directory containing config files, defaults to USER-FILES/01.CONFIG
        """
        if config_dir is None:
            config_dir = Path("USER-FILES/01.CONFIG")
        self.config_dir = Path(config_dir)
        self.config: Dict[str, Any] = {}

    def load_config(self) -> Dict[str, Any]:
        """
        Load main configuration from config.yaml.

        Returns:
            Configuration dictionary

        Raises:
            FileNotFoundError: If config.yaml not found
            yaml.YAMLError: If config is invalid
        """
        config_path = self.config_dir / "config.yaml"

        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        try:
            with open(config_path, "r") as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {config_path}")
            return self.config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in {config_path}: {e}")

    def load_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all raw profiles.

        Returns:
            Dictionary of profile contents
        """
        profiles_dir = Path("USER-FILES/03.PROFILES")
        discovery = InputDiscovery(Path("USER-FILES/04.INPUT"), profiles_dir)
        return discovery.discover_profiles()

    def load_active_profile(self) -> Dict[str, Any]:
        """
        Load exactly one active profile. Searches 03.PROFILES/ first,
        falls back to 01.CONFIG/. Fails fast on 0 or >1 profiles.

        Returns:
            Single profile dictionary

        Raises:
            SystemExit: If 0 or >1 profiles found
        """
        profiles_dir = Path("USER-FILES/03.PROFILES")
        discovery = InputDiscovery(Path("USER-FILES/04.INPUT"), profiles_dir)

        try:
            profiles = discovery.discover_profiles()
        except ValueError:
            logger.warning("No profiles found in 03.PROFILES/, trying 01.CONFIG/...")
            profiles_dir = Path("USER-FILES/01.CONFIG")
            discovery = InputDiscovery(Path("USER-FILES/04.INPUT"), profiles_dir)
            profiles = discovery.discover_profiles()

        active_models = discovery.get_active_models(profiles)

        if len(active_models) == 0:
            logger.error("No valid profiles found in 03.PROFILES/ or 01.CONFIG/")
            sys.exit(1)

        if len(active_models) > 1:
            logger.error(
                f"Multiple profiles found ({len(active_models)}). Keep only ONE."
            )
            sys.exit(1)

        logger.info(f"Using profile: {active_models[0]['profile_name']}")
        return active_models[0]
