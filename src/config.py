import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
LOG_DIR: Path = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

BIGQUERY_SCOPES: list[str] = [
    "https://www.googleapis.com/auth/bigquery",
    "https://www.googleapis.com/auth/cloud-platform",
]

DEFAULT_QUERY_TIMEOUT: int = 300
CACHE_TTL_SECONDS: int = 3600
MAX_CACHE_ENTRIES: int = 100

STREAMLIT_PAGE_TITLE: str = "Panorama da Educacao Basica"
STREAMLIT_LAYOUT: str = "wide"
STREAMLIT_SIDEBAR_STATE: str = "expanded"


def setup_logging(
    name: str = "panorama",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_path = LOG_DIR / (log_file or f"{name}.log")
    file_handler = RotatingFileHandler(
        file_path,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
