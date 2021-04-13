
import os
import sys
from pathlib import Path

import appdirs

HOME = None
APP_NAME = "pysongman"
APP_AUTHOR = "DJW"

HOME = appdirs.user_data_dir(APP_NAME, APP_AUTHOR)
HERE = Path(__file__).parent.absolute()
RSRC_DIR = HERE / "resources"
ICON_DIR = RSRC_DIR / "icons"
CSS_DIR = RSRC_DIR / "css"
