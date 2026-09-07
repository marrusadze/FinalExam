"""
Centralised logging configuration for EventHub.

Writes to logs/app.log (rotating so it doesn't grow forever) and also to the
console. Other modules should just do `import logging` and
`logger = logging.getLogger(__name__)` - this file configures the root
handlers once, on app startup.
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(app):
    log_dir = os.path.join(app.root_path, "..", "logs")
    log_dir = os.path.abspath(log_dir)
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(
        log_file, maxBytes=1_000_000, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Avoid duplicate handlers when the app factory is called more than once
    # (e.g. during tests).
    root_logger.handlers = [file_handler, console_handler]

    app.logger.setLevel(logging.INFO)

    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    app.logger.info("Logging configured. Writing to %s", log_file)
