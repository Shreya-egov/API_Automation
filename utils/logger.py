"""
Logging configuration for API Automation Framework
Provides console and file logging with rotation
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from datetime import datetime


def setup_logger(name=__name__, log_level=logging.INFO):
    """
    Set up logger with console and file handlers

    Args:
        name: Logger name (typically __name__)
        log_level: Logging level (default: INFO)

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Create logs directory if it doesn't exist
    logs_dir = "logs"
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console Handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)

    # File Handler - All logs with rotation (10MB max, keep 5 backups)
    log_file = os.path.join(logs_dir, f'api_automation_{datetime.now().strftime("%Y%m%d")}.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)

    # Error File Handler - Errors only
    error_log_file = os.path.join(logs_dir, f'errors_{datetime.now().strftime("%Y%m%d")}.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    return logger


def log_api_request(logger, method, url, payload=None):
    """Log API request details"""
    logger.info(f"API Request: {method} {url}")
    if payload:
        logger.debug(f"Request Payload: {payload}")


def log_api_response(logger, response):
    """Log API response details"""
    logger.info(f"API Response: Status Code {response.status_code}")
    logger.debug(f"Response Body: {response.text[:500]}...")  # First 500 chars


def log_test_start(logger, test_name):
    """Log test execution start"""
    logger.info("=" * 80)
    logger.info(f"Starting Test: {test_name}")
    logger.info("=" * 80)


def log_test_end(logger, test_name, status="PASSED"):
    """Log test execution end"""
    logger.info("=" * 80)
    logger.info(f"Test {status}: {test_name}")
    logger.info("=" * 80)
