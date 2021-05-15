import appdirs
from pathlib import Path

HERE = Path(__file__).parent
__version__ = "0.0.5"
APP_NAME = "pysongman"
APP_AUTHOR = "DevDave"
HOME = Path(appdirs.user_data_dir(APP_NAME, APP_AUTHOR))
DB_FILE = HOME / f"{APP_NAME}.sqlite3"
CONFIGURED_FLAG = HOME / "installed.txt"
RSRC_DIR = HERE / "resources"
ICON_DIR = RSRC_DIR / "icons"
CSS_DIR = RSRC_DIR / "css"
USE_PYSIDE = True

if HOME.exists() is False:
    HOME.mkdir(parents=True, exist_ok=True)

App = None