import logging
from pathlib import Path
from datetime import datetime


def setup_logger(log_folder: str = "logs") -> logging.Logger:
    """
    Creates a timestamped log file in log_folder.
    Dual output: file (DEBUG+) and console (INFO+).
    Returns the configured logger named "HRAutomation".
    """
    Path(log_folder).mkdir(parents=True, exist_ok=True)

    log_file = Path(log_folder) / f"{datetime.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger("HRAutomation")
    logger.setLevel(logging.DEBUG)

    # Avoid duplicate handlers if logger was already configured
    if logger.handlers:
        logger.handlers.clear()

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.addHandler(fh)
    logger.addHandler(ch)

    logger.info(f"Log file: {log_file}")
    return logger
