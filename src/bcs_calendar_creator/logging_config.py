"""
Logging configuration for the BCS Calendar Creator.
Provides colored console output and configurable log levels.
"""

import logging
import colorlog


def setup_logging(debug=False):
    """
    Configure logging with colored output based on log level.

    Args:
        debug (bool): If True, set log level to DEBUG, otherwise INFO
    """
    # Set log level based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO

    # Create a color formatter
    formatter = colorlog.ColoredFormatter(
        "%(log_color)s[%(name)s]: [%(asctime)s] [%(levelname)s] {%(filename)s:%(lineno)d} %(funcName)s # %(message)s",
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
        secondary_log_colors={},
        style="%",
    )

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove any existing handlers to avoid duplicate logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler and set formatter
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Add handler to logger
    root_logger.addHandler(console_handler)

    return root_logger
