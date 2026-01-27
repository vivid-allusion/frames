"""Input discovery for prompts and profiles."""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Tuple
from loguru import logger
from natsort import natsorted
from src.processing.markdown_parser import extract_prompt_text


class InputDiscovery:
    """Discover and load input files and profiles."""

    def __init__(self, input_dir: Path, profiles_dir: Path):
        """
        Initialize input discovery.

        Args:
            input_dir: Directory containing markdown files
            profiles_dir: Directory containing profile YAML files
        """
        self.input_dir = Path(input_dir)
        self.profiles_dir = Path(profiles_dir)

    def discover_prompt_files(self) -> List[Tuple[Path, Path]]:
        """
        Recursively find all markdown files in input directory.

        Returns:
            List of tuples: (absolute_path, relative_path_from_input)
        """
        prompt_files = []

        if not self.input_dir.exists():
            raise FileNotFoundError(f"Input directory not found: {self.input_dir}")

        # Find all .md files recursively
        for md_file in self.input_dir.rglob("*.md"):
            # Calculate relative path from input directory
            relative_path = md_file.relative_to(self.input_dir)
            prompt_files.append((md_file, relative_path))
            logger.debug(f"Found markdown file: {relative_path}")

        if not prompt_files:
            raise ValueError(f"No .md files found in {self.input_dir}")

        logger.info(f"Discovered {len(prompt_files)} markdown files")
        # Sort by the absolute path for consistent ordering
        return natsorted(prompt_files, key=lambda x: x[0])

    def load_prompts(self, file_path: Path) -> List[str]:
        """
        Load prompt text from markdown file code block.

        Args:
            file_path: Path to markdown file

        Returns:
            List with single prompt string extracted from code block
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            prompt_text = extract_prompt_text(content)
            logger.info(f"Extracted prompt from {file_path.name}")
            return [prompt_text]  # Return as list with single item for compatibility
        except ValueError as e:
            logger.error(f"Failed to extract prompt from {file_path.name}: {e}")
            raise

    def discover_profiles(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all profile YAML files.

        Returns:
            Dictionary mapping profile paths to their contents
        """
        profiles = {}

        if not self.profiles_dir.exists():
            raise FileNotFoundError(
                f"Profiles directory not found: {self.profiles_dir}"
            )

        # Find all .yaml and .yml files
        yaml_files = list(self.profiles_dir.glob("*.yaml"))
        yaml_files.extend(self.profiles_dir.glob("*.yml"))

        if not yaml_files:
            raise ValueError(f"No YAML profiles found in {self.profiles_dir}")

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, "r") as f:
                    profile_data = yaml.safe_load(f) or {}
                profiles[str(yaml_file)] = profile_data
                logger.debug(f"Loaded profile: {yaml_file}")
            except yaml.YAMLError as e:
                raise yaml.YAMLError(f"Invalid YAML in {yaml_file}: {e}")

        logger.info(f"Loaded {len(profiles)} profiles")
        return profiles

    def get_active_models(
        self, profiles: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Extract all models from profiles (all profiles are considered active).

        Args:
            profiles: Dictionary of loaded profiles

        Returns:
            List of dictionaries containing model information for all profiles
        """
        active_models = []

        for profile_path, profile_data in profiles.items():
            profile_name = Path(profile_path).stem  # Get filename without extension

            # Validate required fields - check for model_id (Replicate) or endpoint (legacy)
            model_id = profile_data.get("model_id") or profile_data.get("endpoint")
            if not model_id:
                logger.warning(
                    f"Profile {profile_name} missing 'model_id' field, skipping"
                )
                continue

            active_models.append(
                {
                    "name": profile_name,
                    "model_id": model_id,
                    "endpoint": model_id,  # Keep for backward compatibility
                    "parameters": profile_data.get("parameters", {}),
                    "pricing": profile_data.get("pricing", {}),
                    "description": profile_data.get("description", ""),
                    "profile_name": profile_name,
                    "prompt_prefix": profile_data.get("prompt_prefix", ""),
                    "prompt_suffix": profile_data.get("prompt_suffix", ""),
                    "delay_between_requests": profile_data.get(
                        "delay_between_requests", 0
                    ),
                    "image_input": profile_data.get("image_input", ""),
                    "output_format": profile_data.get("output_format", ""),
                    "project": profile_data.get("project", ""),
                    "paths": profile_data.get("paths", {}),
                }
            )
            logger.info(f"Found profile: {profile_name}")

        if not active_models:
            raise ValueError("No valid profiles found in profiles directory")

        logger.info(f"Total profiles to process: {len(active_models)}")
        return active_models
