
import os
import sys
from pathlib import Path

import appdirs

HOME = None
APP_NAME = "pysongman"
APP_AUTHOR = "DJW"

HOME = Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR))

if HOME.exists() is False:
    HOME.mkdir(parents=True, exist_ok=True)


HERE = Path(__file__).parent.absolute()
RSRC_DIR = HERE / "resources"
ICON_DIR = RSRC_DIR / "icons"
CSS_DIR = RSRC_DIR / "css"
