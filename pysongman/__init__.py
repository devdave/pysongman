"""
    Common/global application values
"""
from pathlib import Path
import appdirs


HERE = Path(__file__).parent
__version__ = "0.0.5"
APP_NAME = "pysongman"
APP_AUTHOR = "DevDave"

HOME = Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR))
DB_FILE = f"{APP_NAME}.sqlite3"
DEFAULT_DB_FILE = HOME / DB_FILE
CONFIGURATION_FLAG = "installed.txt"
DEFAULT_FLAG = HOME / "installed.txt"
RSRC_DIR = HERE / "resources"
ICON_DIR = RSRC_DIR / "icons"
CSS_DIR = RSRC_DIR / "css"
USE_PYSIDE = True

if HOME.exists() is False:
    HOME.mkdir(parents=True, exist_ok=True)

App = None
