"""Replicate API client wrapper with sequential processing."""

import os
import time
import json
from typing import Dict, Any, Optional
from loguru import logger
import replicate
from ..auth.onepassword import get_api_key
from ..constants import (
    DEFAULT_TIMEOUT,
    DEFAULT_MAX_RETRIES,
    DEFAULT_MAX_WAIT_TIME,
    DEFAULT_RATE_LIMIT_RETRY_DELAY,
)


class ReplicateClient:
    """Wrapper for Replicate with sequential processing and error handling."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_wait_time: int = DEFAULT_MAX_WAIT_TIME,
        rate_limit_retry_delay: int = DEFAULT_RATE_LIMIT_RETRY_DELAY,
    ):
        """
        Initialize Replicate client.

        Args:
            api_key: Replicate API token (optional, will use 1Password if not provided)
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            max_wait_time: Max time to wait for predictions
            rate_limit_retry_delay: Delay when rate limited
        """
        # Use provided key or get from 1Password
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = get_api_key()

        self.timeout = timeout
        self.max_retries = max_retries
        self.max_wait_time = max_wait_time
        self.rate_limit_retry_delay = rate_limit_retry_delay

        # Set API token in environment for replicate
        os.environ["REPLICATE_API_TOKEN"] = self.api_key

    def generate_image(
        self, model_id: str, prompt: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate an image using Replicate API with pure parameter pass-through.

        Args:
            model_id: Replicate model identifier
            prompt: Text prompt
            params: All model parameters from profile (passed through unchanged)

        Returns:
            API response dictionary

        Raises:
            Exception: On API failure after retries
        """
        # Build request payload - pure pass-through approach
        clean_prompt = prompt.replace('\\"', '"')

        # Pass all parameters from profile directly to API
        payload = {
            **params,  # All profile parameters passed through unchanged
            "prompt": clean_prompt,
        }

        # CRITICAL DEBUG: Log what we received and what we're sending
        logger.debug(
            f"CRITICAL DEBUG - Received params: {json.dumps(params, indent=2)}"
        )
        logger.debug(
            f"CRITICAL DEBUG - Constructed payload: {json.dumps(payload, indent=2)}"
        )

        # Log the actual prompt being sent
        logger.debug(f"Original prompt: {prompt}")
        logger.debug(f"Clean prompt being sent: {clean_prompt}")
        logger.debug(f"Clean prompt repr: {repr(clean_prompt)}")

        result = self._call_with_retry(model_id, payload)

        return {"result": result, "payload": payload}

    def _call_with_retry(
        self, model_id: str, payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call Replicate API with retry logic.

        Args:
            model_id: Model identifier
            payload: Request payload

        Returns:
            API response dictionary

        Raises:
            Exception: After all retries exhausted
        """
        last_error = None

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.debug(f"API call attempt {attempt}/{self.max_retries}")

                # Log the EXACT payload being sent to replicate.run
                logger.debug(
                    f"CRITICAL DEBUG - Payload sent to replicate.run: {json.dumps(payload, indent=2)}"
                )
                logger.debug(f"Calling replicate.run('{model_id}', input={{...}})")
                logger.debug(f"Input keys: {list(payload.keys())}")

                # Use replicate.run for synchronous execution
                output = replicate.run(model_id, input=payload)

                logger.debug(f"replicate.run() completed successfully!")
                logger.debug(f"Output type: {type(output)}")

                # Convert output to consistent format
                result = self._format_output(output)

                logger.debug("API call successful")
                return result

            except Exception as e:
                last_error = e

                # Check if it's a rate limit error
                if "429" in str(e) or "rate" in str(e).lower():
                    logger.warning(
                        f"Rate limited, waiting {self.rate_limit_retry_delay}s..."
                    )
                    time.sleep(self.rate_limit_retry_delay)
                    continue

                # Other errors
                logger.error(f"Error on attempt {attempt}: {e}")

                if attempt < self.max_retries:
                    wait_time = 2**attempt  # Exponential backoff
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    raise

        # All retries exhausted
        raise Exception(f"Failed after {self.max_retries} attempts: {last_error}")

    def _format_output(self, output: Any) -> Dict[str, Any]:
        """
        Format Replicate output to consistent structure.

        Args:
            output: Raw output from Replicate

        Returns:
            Formatted output dictionary
        """
        # Handle different output formats from Replicate
        if isinstance(output, list):
            # Multiple outputs or single output in list
            images = []
            for item in output:
                if hasattr(item, "read"):
                    # FileOutput object
                    images.append({"url": str(item)})
                else:
                    # URL string
                    images.append({"url": str(item)})
            return {"images": images}
        elif hasattr(output, "read"):
            # Single FileOutput object
            return {"images": [{"url": str(output)}]}
        else:
            # Single URL or other format
            return {"images": [{"url": str(output)}]}
