"""Configuration loading for Replicate wrapper."""
import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class ConfigLoader:
    """Load and manage configuration files."""
    
    def __init__(self, config_dir: Path = None):
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
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
            logger.info(f"Loaded configuration from {config_path}")
            return self.config
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in {config_path}: {e}")
    
    def get_wrapper_config(self) -> Dict[str, Any]:
        """Get wrapper-specific configuration."""
        return self.config.get('wrapper', {})
    
    def get_queue_config(self) -> Dict[str, Any]:
        """Get queue management configuration."""
        return self.config.get('queue', {})
    
    def get_notifications_config(self) -> Dict[str, Any]:
        """Get notifications configuration."""
        return self.config.get('notifications', {})