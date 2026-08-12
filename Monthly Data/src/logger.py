import logging
from pathlib import Path
from datetime import datetime


def setup_logger(log_folder: str):

    Path(log_folder).mkdir(exist_ok=True)

    logfile = Path(log_folder) / f"{datetime.now():%Y%m%d_%H%M%S}.log"

    logging.basicConfig(

        level=logging.INFO,

        format="%(asctime)s | %(levelname)s | %(message)s",

        handlers=[

            logging.FileHandler(logfile),

            logging.StreamHandler()

        ]

    )

    return logging.getLogger("TopicReport")