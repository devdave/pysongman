import sys
import logging
import argparse
import pathlib

TEMP_HOME = pathlib.Path(__file__).parent / ".." / ".." / "temp_home"

assert TEMP_HOME.exists()

import pysongman
from pysongman.lib.application import Application
from pysongman.models import initialize_db, get_db, get_db_url
from pysongman.controllers.media import MediaController


log = logging.getLogger(__name__)


def main():

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    app = Application(here=pysongman.HERE, home=TEMP_HOME, configured_file=pysongman.CONFIGURATION_FLAG)
    app.configure(nuke_everything=False, debug_flag=True, run=False)

    media = MediaController()
    media.signals.new_playlist.connect(lambda sids: log.debug("Got %s", sids))

    media.show()
    app.exec_()



if __name__ == '__main__':
    main()