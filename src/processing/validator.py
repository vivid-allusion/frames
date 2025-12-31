"""Generic validation logic for processing."""
from typing import Dict, Any, List
from loguru import logger
from ..exceptions import ValidationError


class GenericValidator:
    """Validates non-parameter processing requirements."""

    def validate_operational_requirements(self, active_models: List[Dict[str, Any]]) -> None:
        """Validate only operational requirements, not parameters."""
        # Only validate that profiles have required structure
        for model in active_models:
            profile_name = model.get('profile_name', 'unknown')
            
            # Check required profile fields exist
            if not model.get('endpoint'):
                error_msg = f"Profile '{profile_name}' missing required 'endpoint' field"
                logger.error(error_msg)
                raise ValidationError(error_msg)
            
            # Parameters section is optional - API will validate content
            logger.debug(f"Profile '{profile_name}' operational validation passed")
