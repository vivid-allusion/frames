#!/usr/bin/env python3
"""Single-file test for Replicate integration."""
import os
import sys
from pathlib import Path
from loguru import logger

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.api.client import ReplicateClient


def test_replicate():
    """Test basic Replicate functionality with one prompt."""
    
    # Check for API token
    api_token = os.getenv('REPLICATE_API_TOKEN')
    if not api_token:
        logger.error("No REPLICATE_API_TOKEN found in environment")
        sys.exit(1)
    
    logger.info("Starting Replicate test...")
    
    # Initialize client
    client = ReplicateClient(
        api_key=api_token,
        timeout=120,
        max_retries=3
    )
    
    # Test prompt
    test_prompt = "A serene mountain landscape at sunset"
    
    # Test model and parameters
    model_id = "black-forest-labs/flux-schnell"
    params = {
        "num_outputs": 1,
        "aspect_ratio": "16:9",
        "output_format": "webp"
    }
    
    try:
        logger.info(f"Testing with model: {model_id}")
        logger.info(f"Prompt: {test_prompt}")
        
        # Generate image
        response = client.generate_image(
            model_id=model_id,
            prompt=test_prompt,
            params=params,
        )
        
        # Check response
        if 'result' in response and 'images' in response['result']:
            images = response['result']['images']
            logger.success(f"Success! Generated {len(images)} image(s)")
            for i, img in enumerate(images):
                logger.info(f"Image {i+1} URL: {img['url']}")
        else:
            logger.error(f"Unexpected response format: {response}")
            sys.exit(1)
            
        logger.success("Replicate test completed successfully!")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_replicate()