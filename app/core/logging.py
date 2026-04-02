import sys
from loguru import logger

def setup_logging():
    """
    Configure structured logging with loguru.
    Removes the default handler and adds a JSON-formatted one
    so every log line is machine-parseable.
    """
    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
        level="INFO",
        colorize=True,
    )
    logger.add(
        "logs/app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{line} | {message}",
        level="INFO",
        rotation="10 MB",
        retention="7 days",
        serialize=True,
    )

def get_logger(name: str):
    return logger.bind(name=name)
