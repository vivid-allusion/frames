"""Logging setup with loguru."""
from pathlib import Path
from loguru import logger
import sys


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """
    Configure logging for the application.
    
    Args:
        verbose: Enable verbose console output
        debug: Enable debug level logging
    """
    # Remove default handler
    logger.remove()
    
    # Console handler
    level = "DEBUG" if debug else ("INFO" if verbose else "WARNING")
    logger.add(
        sys.stderr,
        format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        level=level,
        colorize=True
    )
    
    # File handler with rotation
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logger.add(
        log_dir / "replicate_wrapper_{time}.log",
        rotation="10 MB",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    logger.info(f"Logging configured (verbose={verbose}, debug={debug})")