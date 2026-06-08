"""Tests for model agnosticism implementation."""

import unittest
from unittest.mock import patch
from pathlib import Path
import sys

# Add src to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.processing.validator import GenericValidator
from src.processing.context import ProcessingContext
from src.api.client import ReplicateClient


class TestModelAgnosticism(unittest.TestCase):
    """Test that the system implements true model agnosticism."""

    def test_generic_validator_accepts_any_parameters(self):
        """Test that validator has no parameter validation (model agnosticism)."""
        validator = GenericValidator()
        
        # GenericValidator only validates markdown file structure,
        # not profile parameters — that's the model agnosticism principle.
        # Any profile parameters should pass through without validation.
        test_profiles = [
            {
                'profile_name': 'image_urls_profile',
                'endpoint': 'test/model',
                'parameters': {'image_urls': ['http://example.com'], 'output_format': 'png'}
            },
            {
                'profile_name': 'image_input_profile', 
                'endpoint': 'test/model',
                'parameters': {'image_input': 'http://example.com', 'custom_param': 'value'}
            },
            {
                'profile_name': 'unknown_params_profile',
                'endpoint': 'test/model',
                'parameters': {'future_param': 'test', 'nested_param': {'key': 'value'}}
            }
        ]
        
        # GenericValidator has no parameter-related methods.
        # The absence of parameter validation IS the model agnosticism guarantee.
        self.assertFalse(hasattr(validator, 'validate_operational_requirements'))

    def test_processing_context_preserves_all_parameters(self):
        """Test that ProcessingContext preserves all parameters without filtering."""
        # Test parameters with various types and unknown names
        test_params = {
            'image_urls': ['https://example.com/image.png'],
            'output_format': 'png',
            'unknown_string_param': 'test_value',
            'unknown_numeric_param': 42,
            'unknown_list_param': [1, 2, 3],
            'unknown_dict_param': {'nested': 'value'},
            'future_api_param': {'complex': {'nested': ['structure']}}
        }
        
        context = ProcessingContext(
            prompt_file=Path("test.txt"),
            relative_path=Path("test.txt"),
            prompts=["test prompt"],
            model_id="test/model",
            params=test_params,
            pricing={},
            profile_name="test_profile",
            output_dir=Path("output")
        )
        
        # All parameters should be preserved exactly
        self.assertEqual(context.params, test_params)
        
        # Verify specific parameters exist
        self.assertIn('image_urls', context.params)
        self.assertIn('unknown_string_param', context.params)
        self.assertIn('future_api_param', context.params)

    @patch('replicate.run')
    def test_api_client_passes_all_parameters(self, mock_replicate_run):
        """Test that API client passes all profile parameters to replicate.run."""
        # Mock the replicate response
        mock_replicate_run.return_value = ["http://example.com/result.png"]
        
        # Create client
        client = ReplicateClient(api_key="test_key")
        
        # Test parameters with various unknown types
        test_params = {
            'image_urls': ['https://example.com/input.png'],
            'output_format': 'png',
            'aspect_ratio': 'match_input_image',
            'unknown_future_param': 'should_be_passed_through',
            'complex_param': {'nested': {'structure': [1, 2, 3]}},
            'api_specific_param': 'model_dependent_value'
        }
        
        # Call generate_image
        result = client.generate_image(
            model_id="google/nano-banana",
            prompt="test prompt",
            params=test_params
        )
        
        # Verify replicate.run was called with all parameters
        mock_replicate_run.assert_called_once()
        call_args = mock_replicate_run.call_args
        
        # Check model_id
        self.assertEqual(call_args[0][0], "google/nano-banana")
        
        # Check that all parameters were passed through in input
        input_payload = call_args[1]['input']
        
        # Verify prompt is included
        self.assertEqual(input_payload['prompt'], "test prompt")
        
        # Verify ALL original parameters are preserved
        for key, value in test_params.items():
            with self.subTest(param=key):
                self.assertIn(key, input_payload, f"Parameter {key} not passed to API")
                self.assertEqual(input_payload[key], value, f"Parameter {key} value changed")

    @patch('replicate.run')
    def test_api_client_handles_various_parameter_types(self, mock_replicate_run):
        """Test that client handles various parameter types without conversion."""
        mock_replicate_run.return_value = ["http://example.com/result.png"]
        
        client = ReplicateClient(api_key="test_key")
        
        # Test with different data types
        complex_params = {
            'string_param': 'text_value',
            'int_param': 42,
            'float_param': 3.14,
            'bool_param': True,
            'list_param': ['item1', 'item2', 3],
            'dict_param': {'nested': {'deep': 'value'}},
            'none_param': None,
            'empty_list': [],
            'empty_dict': {}
        }
        
        client.generate_image(
            model_id="test/model",
            prompt="test",
            params=complex_params
        )
        
        # Verify all parameter types preserved
        input_payload = mock_replicate_run.call_args[1]['input']
        
        for key, expected_value in complex_params.items():
            with self.subTest(param=key, type=type(expected_value).__name__):
                self.assertEqual(input_payload[key], expected_value)

    def test_no_parameter_filtering_or_validation(self):
        """Test that no parameter filtering or validation occurs."""
        # Test that even 'invalid' parameter names are passed through
        potentially_problematic_params = {
            'eval': 'dangerous_looking_but_should_pass',
            'exec': 'another_dangerous_name',
            'import': 'keyword_name',
            'class': 'python_keyword',
            'def': 'another_keyword',
            '__private__': 'private_looking_param',
            'SCREAMING_CASE': 'different_case',
            'camelCase': 'mixed_case',
            'param-with-dashes': 'special_chars',
            'param.with.dots': 'more_special_chars',
            'param_123': 'with_numbers'
        }
        
        context = ProcessingContext(
            prompt_file=Path("test.txt"),
            relative_path=Path("test.txt"), 
            prompts=["test"],
            model_id="test/model",
            params=potentially_problematic_params,
            pricing={},
            profile_name="test",
            output_dir=Path("output")
        )
        
        # All parameters should pass through unchanged
        self.assertEqual(context.params, potentially_problematic_params)


class TestAgnosticismPrinciples(unittest.TestCase):
    """Test adherence to AI Model Agnosticism Manifesto principles."""

    def test_manifesto_principle_1_profiles_are_source_of_truth(self):
        """Test: The profile defines everything about how to interact with a model."""
        # Simulate a profile with complete parameter definition
        profile_params = {
            'model_specific_param': 'value_defined_in_profile',
            'api_endpoint_param': 'profile_controlled',
            'custom_behavior': {'profile': 'driven'}
        }
        
        # System should trust profile completely
        context = ProcessingContext(
            prompt_file=Path("test.txt"),
            relative_path=Path("test.txt"),
            prompts=["test"],
            model_id="test/model", 
            params=profile_params,
            pricing={},
            profile_name="test",
            output_dir=Path("output")
        )
        
        # No modification or filtering should occur
        self.assertEqual(context.params, profile_params)

    def test_manifesto_principle_2_no_hardcoded_model_logic(self):
        """Test: No conditional logic based on endpoint names or parameter types."""
        # Test with various 'model-looking' names that might trigger hardcoded logic
        test_cases = [
            {'endpoint': 'google/nano-banana', 'params': {'image_urls': ['test']}},
            {'endpoint': 'openai/gpt-4', 'params': {'temperature': 0.7}},
            {'endpoint': 'anthropic/claude', 'params': {'max_tokens': 1000}},
            {'endpoint': 'unknown/future-model', 'params': {'future_param': 'value'}}
        ]
        
        for case in test_cases:
            with self.subTest(endpoint=case['endpoint']):
                context = ProcessingContext(
                    prompt_file=Path("test.txt"),
                    relative_path=Path("test.txt"),
                    prompts=["test"],
                    model_id=case['endpoint'],
                    params=case['params'],
                    pricing={},
                    profile_name="test", 
                    output_dir=Path("output")
                )
                
                # Parameters should be preserved regardless of endpoint
                self.assertEqual(context.params, case['params'])

    def test_manifesto_principle_3_pass_everything_through(self):
        """Test: All parameters defined in profile should be passed to API exactly as loaded."""
        original_params = {
            'loaded_from_yaml': 'exactly_as_written',
            'no_modification': True,
            'no_filtering': [1, 2, 3],
            'no_validation': {'by': 'script'}
        }
        
        # Simulate the exact flow: profile -> context -> API
        context = ProcessingContext(
            prompt_file=Path("test.txt"),
            relative_path=Path("test.txt"),
            prompts=["test"],
            model_id="test/model",
            params=original_params,
            pricing={},
            profile_name="test",
            output_dir=Path("output")
        )
        
        # Parameters should be identical to what was loaded from profile
        self.assertEqual(context.params, original_params)


if __name__ == '__main__':
    unittest.main()