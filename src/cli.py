"""Command line interface argument parsing."""
import argparse


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Replicate Image Generation Wrapper"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Test without making API calls"
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output"
    )

    parser.add_argument(
        "--cost-estimation",
        action="store_true",
        help="Estimate costs without generating"
    )

    parser.add_argument(
        "--no-progress",
        action="store_true",
        help="Disable progress bar"
    )

    parser.add_argument(
        "--force-png",
        action="store_true",
        help="Convert all images to PNG format"
    )

    parser.add_argument(
        "--no-save-payloads",
        action="store_false",
        dest="save_payloads",
        help="Disable saving JSON payloads for each request"
    )

    parser.set_defaults(save_payloads=True)

    return parser.parse_args()