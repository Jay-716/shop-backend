import logging
import sys
from pathlib import Path
from datetime import datetime

from config import LOG_STORAGE_PATH

LOG_STORAGE_PATH = Path(LOG_STORAGE_PATH)
LOG_STORAGE_PATH.mkdir(exist_ok=True)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

stdout_handler = logging.StreamHandler(sys.stdout)
file_handler = logging.FileHandler(LOG_STORAGE_PATH / f"llk-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log")

stdout_handler.setLevel(logging.WARNING)
file_handler.setLevel(logging.DEBUG)

fmt = logging.Formatter("%(name)s: %(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(process)d >>> %(message)s")

stdout_handler.setFormatter(fmt)
file_handler.setFormatter(fmt)

logger.addHandler(stdout_handler)
logger.addHandler(file_handler)
