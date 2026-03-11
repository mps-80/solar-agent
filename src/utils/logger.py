"""
Logging configuration
"""

import logging
import os
from src.utils.config import Config


def get_logger(name: str) -> logging.Logger:
    """
    Get configured logger instance.

    Args:
        name: Logger name (usually __name__)

    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        # File handler
        fh = logging.FileHandler(f"logs/{Config.LOG_FILE}")
        fh.setLevel(getattr(logging, Config.LOG_LEVEL))
        fh.setFormatter(formatter)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, Config.LOG_LEVEL))
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))

    return logger
