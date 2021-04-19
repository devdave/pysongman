
import os
import sys
from pathlib import Path
import logging

log = logging.getLogger(__name__)

import appdirs

HOME = None
APP_NAME = "pysongman"
APP_AUTHOR = "DJW"

HOME = Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR))

if HOME.exists() is False:
    log.debug("Home directory %s doesn't exist, creating.", HOME)
    HOME.mkdir(parents=True, exist_ok=True)

HERE = Path(__file__).parent.absolute()

DB_FILE = HOME / f"{APP_NAME}.sqlite3"
CONFIGURED_FLAG = HOME / "installed.txt"
RSRC_DIR = HERE / "resources"
ICON_DIR = RSRC_DIR / "icons"
CSS_DIR = RSRC_DIR / "css"
