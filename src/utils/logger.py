import logging
import os
from logging.handlers import RotatingFileHandler

from src.config import (
    FILE_LOGS_BACKUP_COUNT,
    FILE_LOGS_ENABLED,
    FILE_LOGS_MAX_BYTES,
    FILE_LOGS_PATH,
)


def setup_logging(level: int = logging.INFO) -> None:
    logging.basicConfig(level=level, format="[%(asctime)s] %(levelname)s:%(name)s: %(message)s")

    if FILE_LOGS_ENABLED:
        try:
            os.makedirs(os.path.dirname(FILE_LOGS_PATH), exist_ok=True)
            file_handler = RotatingFileHandler(
                FILE_LOGS_PATH, maxBytes=FILE_LOGS_MAX_BYTES, backupCount=FILE_LOGS_BACKUP_COUNT
            )
            file_handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s:%(name)s: %(message)s"))
            root_logger = logging.getLogger()
            # Avoid adding multiple duplicate handlers if called twice
            if not any(isinstance(h, RotatingFileHandler) and h.baseFilename == file_handler.baseFilename for h in root_logger.handlers):
                root_logger.addHandler(file_handler)
        except Exception as e:  # pragma: no cover
            logging.getLogger("Aethor").warning(f"Failed to enable file logging: {e}")
